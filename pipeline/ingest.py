"""Ingestion step that pulls supermarket data with supermarket-first priority."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

try:  # pragma: no cover - optional for offline execution
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore[assignment]

from . import REPO_ROOT, WORKING_DIR, ensure_directories, log_event
from .models import RawProduct, StepResult, json_dumps
from .sources.base import ConnectorError
from .sources.supermarkets import build_default_connectors

DATA_ROOT = REPO_ROOT / "data" / "sources"
DEFAULT_OUTPUT = WORKING_DIR / "ingested.csv"


@dataclass
class IngestionConfig:
    """Configuration for the ingestion manager."""

    limit: int = 120
    countries: Sequence[str] = ("PT", "ANG", "CV")
    queries: Mapping[str, Sequence[str]] = field(default_factory=dict)
    prefer_online: Optional[bool] = None


class IngestionManager:
    """Coordinate connectors and merge products with provenance."""

    def __init__(self, config: IngestionConfig) -> None:
        self.config = config
        session = requests.Session() if requests is not None else None
        self.connectors = build_default_connectors(DATA_ROOT, session=session, prefer_online=config.prefer_online)

    # Public -----------------------------------------------------------------
    def collect(self) -> tuple[List[RawProduct], Dict[str, List[dict]], Counter]:
        countries = {c.upper() for c in self.config.countries}
        aggregated: Dict[str, RawProduct] = {}
        provenance: Dict[str, List[dict]] = defaultdict(list)
        metrics: Counter = Counter()

        for connector in self.connectors:
            connector_countries = {c.upper() for c in connector.settings.countries}
            if countries and not countries.intersection(connector_countries):
                continue

            queries = self._queries_for(connector)
            try:
                records = connector.collect(limit=self.config.limit, queries=queries)
            except ConnectorError as exc:
                log_event("ingest", f"Connector {connector.settings.slug} failed: {exc}", status="warning")
                continue

            for record in records:
                metrics[f"source:{connector.settings.slug}"] += 1
                metrics[f"country:{record.country}"] += 1
                mode = "online" if record.extra.get("online") else "offline"
                metrics[f"mode:{mode}"] += 1

                existing = aggregated.get(record.code)
                if existing is None or self._score(record) > self._score(existing):
                    aggregated[record.code] = record

                prov_entry = {
                    "connector": connector.settings.slug,
                    "source": record.source,
                    "country": record.country,
                    "online": bool(record.extra.get("online")),
                    "query": record.extra.get("query"),
                    "last_seen": record.last_seen,
                }
                provenance[record.code].append(prov_entry)

                if len(aggregated) >= self.config.limit:
                    break

            if len(aggregated) >= self.config.limit:
                break

        return list(aggregated.values()), provenance, metrics

    # Helpers ----------------------------------------------------------------
    def _queries_for(self, connector) -> Sequence[str]:
        slug = connector.settings.slug
        if slug in self.config.queries:
            return self.config.queries[slug]
        for country in connector.settings.countries:
            if country in self.config.queries:
                return self.config.queries[country]
        return connector.settings.default_queries

    @staticmethod
    def _score(record: RawProduct) -> tuple[int, float, bool]:
        return (record.priority, record.confidence, bool(record.price))


# CSV ---------------------------------------------------------------------------


def _fieldnames() -> List[str]:
    return [
        "code",
        "product_name",
        "brands",
        "quantity",
        "categories",
        "country",
        "url",
        "source",
        "source_type",
        "confidence",
        "priority",
        "price",
        "currency",
        "availability",
        "last_seen",
        "provenance",
        "extra",
    ]


def write_csv(records: Iterable[RawProduct], provenance: Mapping[str, List[dict]], output: Path) -> int:
    ensure_directories()
    output.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = _fieldnames()
    count = 0
    with output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            row = record.to_csv_row()
            row["provenance"] = json.dumps(provenance.get(record.code, []), ensure_ascii=False)
            writer.writerow(row)
            count += 1
    return count


# Runner -----------------------------------------------------------------------

def run_ingest(config: IngestionConfig, *, output: Path = DEFAULT_OUTPUT) -> StepResult:
    manager = IngestionManager(config)
    records, provenance, metrics = manager.collect()
    records = sorted(records, key=lambda r: r.code)
    total_written = write_csv(records, provenance, output)

    metrics_summary: Dict[str, dict] = {"source": {}, "country": {}, "mode": {}}
    for key, value in metrics.items():
        prefix, name = key.split(":", 1)
        metrics_summary[prefix][name] = value

    result = StepResult(
        name="ingest",
        status="ok" if total_written else "empty",
        metrics={
            "total_records": total_written,
            "sources": metrics_summary["source"],
            "countries": metrics_summary["country"],
            "mode": metrics_summary["mode"],
        },
        artifacts={"csv": str(output)},
        logs=[f"Connector totals: {json_dumps(metrics_summary['source'])}"],
    )
    log_event("ingest", f"Collected {total_written} products from connectors.", extra=result.metrics)
    return result


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest supermarket data for the smart-mode pipeline.")
    parser.add_argument("--limit", type=int, default=120, help="Maximum number of unique products to ingest.")
    parser.add_argument(
        "--country",
        dest="countries",
        action="append",
        default=["PT", "ANG", "CV"],
        help="Country code to include (can be specified multiple times).",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Disable online collection and rely on bundled offline fixtures.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output CSV path (default: artifacts/working/ingested.csv).",
    )
    args = parser.parse_args(argv)

    config = IngestionConfig(
        limit=args.limit,
        countries=[c.upper() for c in args.countries],
        prefer_online=None if not args.offline else False,
    )
    run_ingest(config, output=args.out)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
