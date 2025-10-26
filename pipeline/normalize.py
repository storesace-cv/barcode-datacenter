"""Normalization step bridging raw ingestion to classified data."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import List

from scripts.python.normalize_products import norm, split_qty

from . import WORKING_DIR, ensure_directories, log_event

CURRENCY_BY_COUNTRY = {
    "PT": "EUR",
    "ANG": "AOA",
    "CV": "CVE",
}


def normalize_file(input_path: Path, output_path: Path, fallback_country: str) -> int:
    ensure_directories()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with input_path.open("r", newline="", encoding="utf-8") as src, output_path.open(
        "w", newline="", encoding="utf-8"
    ) as dst:
        reader = csv.DictReader(src)
        fieldnames = [
            "gtin",
            "name",
            "brand",
            "qty",
            "uom",
            "country",
            "source",
            "url",
            "price",
            "currency",
            "category_raw",
            "family",
            "subfamily",
        ]
        writer = csv.DictWriter(dst, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            gtin = (row.get("code") or "").strip()
            country = (row.get("country") or fallback_country).strip().upper() or fallback_country
            qty, uom = split_qty(row.get("quantity", ""))
            writer.writerow(
                {
                    "gtin": gtin,
                    "name": norm(row.get("product_name", "")),
                    "brand": norm(row.get("brands", "")),
                    "qty": qty,
                    "uom": uom,
                    "country": country,
                    "source": row.get("source", "INGEST"),
                    "url": row.get("url", ""),
                    "price": row.get("price", ""),
                    "currency": CURRENCY_BY_COUNTRY.get(country, "EUR"),
                    "category_raw": norm(row.get("categories", "")),
                    "family": "",
                    "subfamily": "",
                }
            )
            count += 1
    return count


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

    count = normalize_file(args.input_path, args.output_path, args.country.upper())
    log_event("normalize", f"Normalized {count} rows.", extra={"output": str(args.output_path)})
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
