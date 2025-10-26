"""Connector infrastructure for retrieving supermarket and open-data products."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Set

try:  # pragma: no cover - allow running in offline environments without requests
    import requests
except ImportError:  # pragma: no cover - fallback for tests/offline usage
    requests = None  # type: ignore[assignment]

from ..models import RawProduct, ensure_iso8601

USER_AGENT = "barcode-datacenter/1.0 (+https://github.com/barcode-datacenter)"


class ConnectorError(RuntimeError):
    """Raised when a connector cannot fulfill an online request."""


@dataclass
class ConnectorSettings:
    slug: str
    label: str
    countries: Sequence[str]
    source: str
    source_type: str
    priority: int
    default_queries: Sequence[str] = field(default_factory=tuple)
    offline_file: Optional[str] = None
    prefer_online: bool = True
    per_query_limit: int = 25


class BaseConnector:
    settings: ConnectorSettings

    def __init__(
        self,
        data_root: Path,
        *,
        session: Optional[object] = None,
        prefer_online: Optional[bool] = None,
    ) -> None:
        self.data_root = data_root
        if session is not None:
            self.session = session
        elif requests is not None:
            self.session = requests.Session()
        else:
            self.session = None
        if prefer_online is not None:
            self.settings = dataclass_replace(self.settings, prefer_online=prefer_online)

    # API -----------------------------------------------------------------
    def collect(self, *, limit: int, queries: Optional[Sequence[str]] = None) -> List[RawProduct]:
        queries = list(queries or self.settings.default_queries)
        results: List[RawProduct] = []
        seen_codes: Set[str] = set()
        errors: List[str] = []

        if self.settings.prefer_online:
            for query in queries:
                if len(results) >= limit:
                    break
                remaining = max(0, limit - len(results))
                try:
                    online_records = self._fetch_online(query, remaining)
                except ConnectorError as exc:
                    errors.append(str(exc))
                    continue
                for record in online_records:
                    if record.code in seen_codes:
                        continue
                    seen_codes.add(record.code)
                    results.append(record)
                    if len(results) >= limit:
                        break

        if len(results) < limit:
            offline_records = self._load_offline()
            for record in offline_records:
                if record.code in seen_codes:
                    continue
                seen_codes.add(record.code)
                results.append(record)
                if len(results) >= limit:
                    break

        if not results and errors:
            raise ConnectorError(
                f"{self.settings.slug}: unable to retrieve records online; errors: {'; '.join(errors)}"
            )

        return results

    # Hooks ---------------------------------------------------------------
    def _fetch_online(self, query: str, limit: int) -> List[RawProduct]:
        raise ConnectorError(f"{self.settings.slug}: online collection not implemented")

    def _load_offline(self) -> List[RawProduct]:
        if not self.settings.offline_file:
            return []
        path = self.data_root / self.settings.offline_file
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        records: List[RawProduct] = []
        for payload in data:
            record = self._convert_payload(payload)
            if record:
                records.append(record)
        return records

    # Helpers -------------------------------------------------------------
    def _convert_payload(self, payload: dict) -> Optional[RawProduct]:
        raise NotImplementedError

    def _make_product(
        self,
        *,
        code: str,
        name: str,
        brand: str,
        quantity: str,
        categories: Iterable[str],
        country: str,
        url: str,
        confidence: float,
        priority: int,
        price: Optional[float] = None,
        currency: Optional[str] = None,
        availability: Optional[str] = None,
        last_seen: Optional[str] = None,
        extra: Optional[dict] = None,
    ) -> RawProduct:
        last_seen_iso = ensure_iso8601(last_seen) or None
        return RawProduct(
            code=str(code),
            name=name,
            brand=brand,
            quantity=quantity,
            categories=[c for c in categories if c],
            country=country,
            url=url,
            source=self.settings.source,
            source_type=self.settings.source_type,
            confidence=confidence,
            priority=priority,
            price=price,
            currency=currency,
            availability=availability,
            last_seen=last_seen_iso,
            extra=extra or {},
        )


def dataclass_replace(settings: ConnectorSettings, **kwargs) -> ConnectorSettings:
    data = settings.__dict__.copy()
    data.update(kwargs)
    return ConnectorSettings(**data)


__all__ = [
    "BaseConnector",
    "ConnectorError",
    "ConnectorSettings",
    "USER_AGENT",
]
