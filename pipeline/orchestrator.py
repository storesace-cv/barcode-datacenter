"""Reusable orchestration entry-points for the smart-mode pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Mapping, Optional

from . import OUTPUTS_DIR, WORKING_DIR
from .ingest import IngestionConfig, run_ingest
from .models import PipelineState, StepResult
from .normalize import run_normalize
from .classify import run_classify
from .validate import run_validate
from .dedupe import run_dedupe
from .publish import run_publish


@dataclass
class StepDefinition:
    slug: str
    description: str
    runner: Callable[..., StepResult]
    default_kwargs: Mapping[str, object] = field(default_factory=dict)


DEFAULT_STEPS: List[StepDefinition] = [
    StepDefinition(
        slug="ingest",
        description="Collect supermarket and open-data sources.",
        runner=lambda **kwargs: run_ingest(IngestionConfig(**kwargs)),
        default_kwargs={"limit": 120, "countries": ("PT", "ANG", "CV"), "prefer_online": None},
    ),
    StepDefinition(
        slug="normalize",
        description="Normalize raw ingestion data into canonical columns.",
        runner=lambda **kwargs: run_normalize(**kwargs),
        default_kwargs={
            "input_path": WORKING_DIR / "ingested.csv",
            "output_path": WORKING_DIR / "normalized.csv",
            "fallback_country": "PT",
        },
    ),
    StepDefinition(
        slug="classify",
        description="Assign taxonomy families and subfamilies.",
        runner=lambda **kwargs: run_classify(**kwargs),
        default_kwargs={
            "input_path": WORKING_DIR / "normalized.csv",
            "output_path": WORKING_DIR / "classified.csv",
        },
    ),
    StepDefinition(
        slug="validate",
        description="Validate GTIN digits and flag invalid barcodes.",
        runner=lambda **kwargs: run_validate(**kwargs),
        default_kwargs={
            "input_path": WORKING_DIR / "classified.csv",
            "output_path": WORKING_DIR / "validated.csv",
        },
    ),
    StepDefinition(
        slug="dedupe",
        description="Merge duplicates prioritising supermarket sources.",
        runner=lambda **kwargs: run_dedupe(**kwargs),
        default_kwargs={
            "input_path": WORKING_DIR / "validated.csv",
            "output_path": WORKING_DIR / "unified.csv",
            "report_path": WORKING_DIR / "duplicates.csv",
        },
    ),
    StepDefinition(
        slug="publish",
        description="Publish unified artifacts to CSV/JSONL/SQLite.",
        runner=lambda **kwargs: run_publish(**kwargs),
        default_kwargs={
            "input_path": WORKING_DIR / "unified.csv",
            "output_dir": OUTPUTS_DIR,
        },
    ),
]


class SmartPipelineRunner:
    """Execute steps sequentially while capturing structured results."""

    def __init__(self, steps: Iterable[StepDefinition] = DEFAULT_STEPS) -> None:
        self.steps: Dict[str, StepDefinition] = {step.slug: step for step in steps}
        self.order: List[str] = [step.slug for step in steps]
        self.state = PipelineState()

    def run_step(self, slug: str, **overrides) -> StepResult:
        if slug not in self.steps:
            raise KeyError(f"Unknown step: {slug}")
        definition = self.steps[slug]
        kwargs = dict(definition.default_kwargs)
        kwargs.update(overrides)
        result = definition.runner(**kwargs)
        self.state.record(result)
        return result

    def run_all(self, overrides: Optional[Mapping[str, Mapping[str, object]]] = None) -> List[StepResult]:
        results: List[StepResult] = []
        override_map = overrides or {}
        for slug in self.order:
            step_overrides = override_map.get(slug, {}) if override_map else {}
            results.append(self.run_step(slug, **step_overrides))
        return results

    def status(self) -> Dict[str, Dict[str, object]]:
        return self.state.to_status()


__all__ = ["SmartPipelineRunner", "StepDefinition", "DEFAULT_STEPS"]
