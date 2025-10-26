"""Shared dataclasses and helpers for the smart-mode pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, Iterable, List, Mapping, Optional

ISO8601 = "%Y-%m-%dT%H:%M:%SZ"


@dataclass
class RawProduct:
    code: str
    name: str
    brand: str
    quantity: str
    categories: List[str]
    country: str
    url: str
    source: str
    source_type: str
    confidence: float
    priority: int
    price: Optional[float] = None
    currency: Optional[str] = None
    availability: Optional[str] = None
    last_seen: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_csv_row(self) -> Dict[str, Any]:
        categories = "; ".join(self.categories)
        return {
            "code": self.code,
            "product_name": self.name,
            "brands": self.brand,
            "quantity": self.quantity,
            "categories": categories,
            "country": self.country,
            "url": self.url,
            "source": self.source,
            "source_type": self.source_type,
            "confidence": f"{self.confidence:.2f}",
            "priority": str(self.priority),
            "price": f"{self.price:.2f}" if self.price is not None else "",
            "currency": self.currency or "",
            "availability": self.availability or "",
            "last_seen": self.last_seen or "",
            "extra": json_dumps(self.extra),
        }


@dataclass
class StepResult:
    name: str
    status: str
    metrics: Dict[str, Any] = field(default_factory=dict)
    artifacts: Dict[str, str] = field(default_factory=dict)
    logs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["ts"] = datetime.utcnow().strftime(ISO8601)
        return payload


@dataclass
class PipelineState:
    results: Dict[str, StepResult] = field(default_factory=dict)

    def record(self, result: StepResult) -> None:
        self.results[result.name] = result

    def to_status(self) -> Dict[str, Any]:
        return {name: result.to_dict() for name, result in self.results.items()}


def json_dumps(data: Mapping[str, Any] | Iterable[tuple[str, Any]] | None) -> str:
    if not data:
        return ""
    import json

    return json.dumps(data, ensure_ascii=False, sort_keys=True)


def ensure_iso8601(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value
    except ValueError:
        return None


__all__ = ["RawProduct", "StepResult", "PipelineState", "json_dumps", "ensure_iso8601"]
