"""Normalization step bridging raw ingestion to classified data."""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import List, Optional

from scripts.python.normalize_products import norm, split_qty

from . import WORKING_DIR, ensure_directories, log_event
from .models import StepResult

CURRENCY_BY_COUNTRY = {
    "PT": "EUR",
    "ANG": "AOA",
    "AO": "AOA",
    "CV": "CVE",
}


FIELDNAMES = [
    "gtin",
    "name",
    "brand",
    "qty",
    "uom",
    "country",
    "source",
    "source_type",
    "confidence",
    "priority",
    "url",
    "price_amount",
    "price_currency",
    "availability",
    "last_seen",
    "category_raw",
    "family",
    "subfamily",
    "provenance",
    "extra",
]


def _normalize_price(value: str) -> Optional[str]:
    if not value:
        return None
    try:
        quantized = Decimal(value).quantize(Decimal("0.01"))
        return f"{quantized:.2f}"
    except (InvalidOperation, ValueError):
        return None


def normalize_file(input_path: Path, output_path: Path, fallback_country: str) -> int:
    ensure_directories()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with input_path.open("r", newline="", encoding="utf-8") as src, output_path.open(
        "w", newline="", encoding="utf-8"
    ) as dst:
        reader = csv.DictReader(src)
        writer = csv.DictWriter(dst, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in reader:
            gtin = (row.get("code") or "").strip()
            country = (row.get("country") or fallback_country).strip().upper() or fallback_country
            qty, uom = split_qty(row.get("quantity", ""))
            price_amount = _normalize_price(row.get("price", ""))
            currency = row.get("currency") or CURRENCY_BY_COUNTRY.get(country, "EUR")
            writer.writerow(
                {
                    "gtin": gtin,
                    "name": norm(row.get("product_name", "")),
                    "brand": norm(row.get("brands", "")),
                    "qty": qty,
                    "uom": uom,
                    "country": country,
                    "source": row.get("source", "INGEST"),
                    "source_type": row.get("source_type", "unknown"),
                    "confidence": row.get("confidence", ""),
                    "priority": row.get("priority", ""),
                    "url": row.get("url", ""),
                    "price_amount": price_amount or "",
                    "price_currency": currency,
                    "availability": row.get("availability", ""),
                    "last_seen": row.get("last_seen", ""),
                    "category_raw": norm(row.get("categories", "")),
                    "family": "",
                    "subfamily": "",
                    "provenance": row.get("provenance", ""),
                    "extra": row.get("extra", ""),
                }
            )
            count += 1
    return count


def run_normalize(
    input_path: Path = WORKING_DIR / "ingested.csv",
    output_path: Path = WORKING_DIR / "normalized.csv",
    fallback_country: str = "PT",
) -> StepResult:
    count = normalize_file(input_path, output_path, fallback_country)
    result = StepResult(
        name="normalize",
        status="ok" if count else "empty",
        metrics={"normalized": count},
        artifacts={"csv": str(output_path)},
    )
    log_event("normalize", f"Normalized {count} rows.", extra=result.metrics)
    return result


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize ingested records into canonical columns.")
    parser.add_argument(
        "--in",
        dest="input_path",
        type=Path,
        default=WORKING_DIR / "ingested.csv",
        help="Input CSV from the ingest step.",
    )
    parser.add_argument(
        "--out",
        dest="output_path",
        type=Path,
        default=WORKING_DIR / "normalized.csv",
        help="Output CSV path (default: artifacts/working/normalized.csv).",
    )
    parser.add_argument("--country", default="PT", help="Fallback country code used when missing in the source data.")
    args = parser.parse_args(argv)

    run_normalize(args.input_path, args.output_path, args.country.upper())
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
