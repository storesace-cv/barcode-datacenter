"""Supermarket-first connectors used by the ingestion step."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional

try:  # pragma: no cover - optional dependency
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore[assignment]

from .base import BaseConnector, ConnectorError, ConnectorSettings, USER_AGENT, dataclass_replace
from ..models import RawProduct

DATA_FOLDER = "supermarkets"


def _price_from_payload(payload: Dict, *keys: str) -> Optional[float]:
    for key in keys:
        value = payload
        for part in key.split("."):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break
        if value in (None, ""):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


class ContinentePTConnector(BaseConnector):
    API_URL = "https://www.continente.pt/api/catalog/search"

    settings = ConnectorSettings(
        slug="continente_pt",
        label="Continente Portugal",
        countries=("PT",),
        source="CONTINENTE_PT",
        source_type="supermarket",
        priority=90,
        default_queries=("arroz", "leite", "azeite"),
        offline_file=f"{DATA_FOLDER}/continente_pt_sample.json",
        prefer_online=True,
        per_query_limit=30,
    )

    def _fetch_online(self, query: str, limit: int) -> List[RawProduct]:
        if getattr(self, "session", None) is None:
            raise ConnectorError("requests não disponível para recolha online")
        params = {
            "text": query,
            "page": 1,
            "pageSize": min(limit or self.settings.per_query_limit, self.settings.per_query_limit),
            "sortBy": "relevance",
        }
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        resp = self.session.get(self.API_URL, params=params, headers=headers, timeout=15)
        if resp.status_code != 200:
            raise ConnectorError(f"continente_pt online request failed: {resp.status_code}")
        data = resp.json()
        items = data.get("products") or data.get("items") or []
        results: List[RawProduct] = []
        for item in items:
            code = item.get("ean") or item.get("gtin") or item.get("code") or item.get("id")
            if not code:
                continue
            name = item.get("name") or item.get("description") or ""
            brand = item.get("brand") or item.get("brandName") or ""
            quantity = item.get("packaging") or item.get("size") or item.get("unit") or ""
            categories = item.get("categories") or item.get("breadcrumbs") or []
            if isinstance(categories, str):
                categories = [c.strip() for c in categories.split(">") if c.strip()]
            price = _price_from_payload(item, "price", "price.current")
            url = item.get("url") or item.get("productUrl") or ""
            availability = item.get("stockStatus") or item.get("availability") or ""
            last_seen = item.get("lastUpdated") or item.get("lastSeen") or datetime.utcnow().isoformat() + "Z"
            product = self._make_product(
                code=code,
                name=name,
                brand=brand,
                quantity=quantity,
                categories=categories,
                country="PT",
                url=url or f"https://www.continente.pt/pesquisa/?q={query}",
                confidence=0.9,
                priority=self.settings.priority,
                price=price,
                currency="EUR",
                availability=availability,
                last_seen=last_seen,
                extra={"query": query, "online": True},
            )
            results.append(product)
            if len(results) >= limit:
                break
        if not results:
            raise ConnectorError("continente_pt returned no products")
        return results

    def _convert_payload(self, payload: dict) -> Optional[RawProduct]:
        code = payload.get("code")
        if not code:
            return None
        return self._make_product(
            code=code,
            name=payload.get("name", ""),
            brand=payload.get("brand", ""),
            quantity=payload.get("quantity", ""),
            categories=payload.get("categories", []),
            country="PT",
            url=payload.get("url", ""),
            confidence=0.85,
            priority=self.settings.priority,
            price=payload.get("price"),
            currency=payload.get("currency", "EUR"),
            availability=payload.get("availability"),
            last_seen=payload.get("last_seen"),
            extra={"query": "offline"},
        )


class ShopriteAngolaConnector(BaseConnector):
    API_URL = "https://www.shoprite.co.ao/api/catalog/search"

    settings = ConnectorSettings(
        slug="shoprite_ao",
        label="Shoprite Angola",
        countries=("AO", "ANG"),
        source="SHOPRITE_AO",
        source_type="supermarket",
        priority=85,
        default_queries=("arroz", "oleo", "leite"),
        offline_file=f"{DATA_FOLDER}/shoprite_ao_sample.json",
        prefer_online=True,
        per_query_limit=30,
    )

    def _fetch_online(self, query: str, limit: int) -> List[RawProduct]:
        if getattr(self, "session", None) is None:
            raise ConnectorError("requests não disponível para recolha online")
        params = {
            "q": query,
            "page": 1,
            "pageSize": min(limit or self.settings.per_query_limit, self.settings.per_query_limit),
        }
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        resp = self.session.get(self.API_URL, params=params, headers=headers, timeout=15)
        if resp.status_code != 200:
            raise ConnectorError(f"shoprite_ao online request failed: {resp.status_code}")
        data = resp.json()
        items = data.get("items") or data.get("products") or []
        results: List[RawProduct] = []
        for item in items:
            code = item.get("ean") or item.get("barcode") or item.get("code")
            if not code:
                continue
            price = _price_from_payload(item, "price", "price.value", "price.current")
            product = self._make_product(
                code=code,
                name=item.get("name", ""),
                brand=item.get("brand", ""),
                quantity=item.get("unit", ""),
                categories=item.get("breadcrumbs", []) or item.get("categories", []),
                country="ANG",
                url=item.get("url", "") or f"https://www.shoprite.co.ao/search?q={query}",
                confidence=0.88,
                priority=self.settings.priority,
                price=price,
                currency="AOA",
                availability=item.get("availability", ""),
                last_seen=item.get("updated_at") or item.get("last_seen"),
                extra={"query": query, "online": True},
            )
            results.append(product)
            if len(results) >= limit:
                break
        if not results:
            raise ConnectorError("shoprite_ao returned no products")
        return results

    def _convert_payload(self, payload: dict) -> Optional[RawProduct]:
        code = payload.get("code")
        if not code:
            return None
        return self._make_product(
            code=code,
            name=payload.get("name", ""),
            brand=payload.get("brand", ""),
            quantity=payload.get("quantity", ""),
            categories=payload.get("categories", []),
            country="ANG",
            url=payload.get("url", ""),
            confidence=0.82,
            priority=self.settings.priority,
            price=payload.get("price"),
            currency=payload.get("currency", "AOA"),
            availability=payload.get("availability"),
            last_seen=payload.get("last_seen"),
            extra={"query": "offline"},
        )


class NosSuperCVConnector(BaseConnector):
    API_URL = "https://www.nossuper.cv/api/catalog/search"

    settings = ConnectorSettings(
        slug="nossuper_cv",
        label="NosSuper Cabo Verde",
        countries=("CV",),
        source="NOSSUPER_CV",
        source_type="supermarket",
        priority=80,
        default_queries=("atum", "feijao", "agua"),
        offline_file=f"{DATA_FOLDER}/nossuper_cv_sample.json",
        prefer_online=True,
        per_query_limit=30,
    )

    def _fetch_online(self, query: str, limit: int) -> List[RawProduct]:
        if getattr(self, "session", None) is None:
            raise ConnectorError("requests não disponível para recolha online")
        params = {"q": query, "page": 1, "pageSize": min(limit or 30, 30)}
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        resp = self.session.get(self.API_URL, params=params, headers=headers, timeout=15)
        if resp.status_code != 200:
            raise ConnectorError(f"nossuper_cv online request failed: {resp.status_code}")
        data = resp.json()
        items = data.get("products") or data.get("items") or []
        results: List[RawProduct] = []
        for item in items:
            code = item.get("ean") or item.get("barcode") or item.get("code")
            if not code:
                continue
            price = _price_from_payload(item, "price", "price.value")
            product = self._make_product(
                code=code,
                name=item.get("name", ""),
                brand=item.get("brand", ""),
                quantity=item.get("unit", ""),
                categories=item.get("categories", []),
                country="CV",
                url=item.get("url", "") or f"https://www.nossuper.cv/pesquisa?q={query}",
                confidence=0.85,
                priority=self.settings.priority,
                price=price,
                currency="CVE",
                availability=item.get("availability", ""),
                last_seen=item.get("updated_at") or item.get("last_seen"),
                extra={"query": query, "online": True},
            )
            results.append(product)
            if len(results) >= limit:
                break
        if not results:
            raise ConnectorError("nossuper_cv returned no products")
        return results

    def _convert_payload(self, payload: dict) -> Optional[RawProduct]:
        code = payload.get("code")
        if not code:
            return None
        return self._make_product(
            code=code,
            name=payload.get("name", ""),
            brand=payload.get("brand", ""),
            quantity=payload.get("quantity", ""),
            categories=payload.get("categories", []),
            country="CV",
            url=payload.get("url", ""),
            confidence=0.8,
            priority=self.settings.priority,
            price=payload.get("price"),
            currency=payload.get("currency", "CVE"),
            availability=payload.get("availability"),
            last_seen=payload.get("last_seen"),
            extra={"query": "offline"},
        )


class OpenFoodFactsFallback(BaseConnector):
    API_URL = "https://world.openfoodfacts.org/cgi/search.pl"

    settings = ConnectorSettings(
        slug="openfoodfacts",
        label="Open Food Facts",
        countries=("PT", "ANG", "CV"),
        source="OPEN_FOOD_FACTS",
        source_type="open-data",
        priority=50,
        default_queries=("portugal", "cabo verde", "angola"),
        offline_file="openfoodfacts_sample.json",
        prefer_online=False,
        per_query_limit=100,
    )

    def _fetch_online(self, query: str, limit: int) -> List[RawProduct]:
        if getattr(self, "session", None) is None:
            raise ConnectorError("requests não disponível para recolha online")
        params = {
            "search_terms": query,
            "search_simple": 1,
            "json": 1,
            "page_size": min(limit or self.settings.per_query_limit, self.settings.per_query_limit),
            "fields": "code,product_name,brands,quantity,categories,countries,url,last_modified_t",
        }
        resp = self.session.get(self.API_URL, params=params, headers={"User-Agent": USER_AGENT}, timeout=15)
        if resp.status_code != 200:
            raise ConnectorError(f"openfoodfacts online request failed: {resp.status_code}")
        data = resp.json()
        items = data.get("products") or []
        results: List[RawProduct] = []
        for item in items:
            code = item.get("code")
            if not code:
                continue
            categories = (item.get("categories") or "").split(",")
            countries = (item.get("countries") or "").upper()
            country = "PT"
            if "ANGOLA" in countries:
                country = "ANG"
            elif "CABO VERDE" in countries or "CAPE VERDE" in countries:
                country = "CV"
            product = self._make_product(
                code=code,
                name=item.get("product_name", ""),
                brand=item.get("brands", ""),
                quantity=item.get("quantity", ""),
                categories=[c.strip() for c in categories if c.strip()],
                country=country,
                url=item.get("url", ""),
                confidence=0.6,
                priority=self.settings.priority,
                price=None,
                currency=None,
                availability=None,
                last_seen=None,
                extra={"query": query, "online": True},
            )
            results.append(product)
            if len(results) >= limit:
                break
        if not results:
            raise ConnectorError("openfoodfacts returned no products")
        return results

    def _convert_payload(self, payload: dict) -> Optional[RawProduct]:
        code = payload.get("code")
        if not code:
            return None
        categories = payload.get("categories")
        if isinstance(categories, str):
            categories = [c.strip() for c in categories.split(",") if c.strip()]
        countries = (payload.get("countries") or "").upper()
        country = "PT"
        if "ANGOLA" in countries:
            country = "ANG"
        elif "CABO VERDE" in countries or "CAPE VERDE" in countries:
            country = "CV"
        last_seen = None
        if payload.get("last_modified_t"):
            try:
                last_seen = datetime.utcfromtimestamp(int(payload["last_modified_t"])).isoformat() + "Z"
            except Exception:
                last_seen = None
        return self._make_product(
            code=code,
            name=payload.get("product_name", ""),
            brand=payload.get("brands", ""),
            quantity=payload.get("quantity", ""),
            categories=categories or [],
            country=country,
            url=payload.get("url", ""),
            confidence=0.5,
            priority=self.settings.priority,
            price=None,
            currency=None,
            availability=None,
            last_seen=last_seen,
            extra={"query": "offline"},
        )


def build_default_connectors(
    data_root: Path,
    *,
    session: Optional[object] = None,
    prefer_online: Optional[bool] = None,
) -> List[BaseConnector]:
    if session is None and requests is not None:
        session = requests.Session()
    connectors: List[BaseConnector] = [
        ContinentePTConnector(data_root, session=session, prefer_online=True),
        ShopriteAngolaConnector(data_root, session=session, prefer_online=True),
        NosSuperCVConnector(data_root, session=session, prefer_online=True),
        OpenFoodFactsFallback(data_root, session=session, prefer_online=False),
    ]
    if prefer_online is not None:
        for connector in connectors:
            connector.settings = dataclass_replace(connector.settings, prefer_online=prefer_online)
    return connectors


__all__ = [
    "build_default_connectors",
    "ContinentePTConnector",
    "ShopriteAngolaConnector",
    "NosSuperCVConnector",
    "OpenFoodFactsFallback",
]
