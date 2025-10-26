"""Ingestion step for the Barcode Datacenter smart-mode pipeline."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from . import WORKING_DIR, ensure_directories, log_event


@dataclass
class RawProduct:
    code: str
    product_name: str
    brands: str
    quantity: str
    categories: str
    country: str
    url: str
    source: str = "OFF_STUB"


SAMPLE_DATA: List[RawProduct] = [
    RawProduct(
        code="5601234567890",
        product_name="Arroz Agulha 1kg",
        brands="Bom Sucesso",
        quantity="1 kg",
        categories="Cereais e derivados, Arroz",
        country="PT",
        url="https://openfoodfacts.org/product/5601234567890",
    ),
    RawProduct(
        code="5609876543210",
        product_name="Água Mineral 1,5L",
        brands="Luso",
        quantity="1.5 l",
        categories="Bebidas, Águas",
        country="PT",
        url="https://openfoodfacts.org/product/5609876543210",
    ),
    RawProduct(
        code="7891234567895",
        product_name="Massa Espaguete 500g",
        brands="Barilla",
        quantity="500 g",
        categories="Massas, Espaguete",
        country="PT",
        url="https://openfoodfacts.org/product/7891234567895",
    ),
]


def cycle_records(limit: int) -> Iterable[RawProduct]:
    """Yield *limit* products cycling over the static sample list."""

    idx = 0
    for i in range(limit):
        base = SAMPLE_DATA[idx % len(SAMPLE_DATA)]
        code = str(int(base.code) + i)
        yield RawProduct(
            code=code,
            product_name=base.product_name,
            brands=base.brands,
            quantity=base.quantity,
            categories=base.categories,
            country=base.country,
            url=base.url,
            source=base.source,
        )
        idx += 1


def write_csv(records: Iterable[RawProduct], output: Path) -> int:
    ensure_directories()
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "code",
        "product_name",
        "brands",
        "quantity",
        "categories",
        "country",
        "url",
        "source",
    ]
    count = 0
    with output.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(record.__dict__)
            count += 1
    return count


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest seed data into the working area.")
    parser.add_argument("--limit", type=int, default=50, help="Number of stub records to generate.")
    parser.add_argument(
        "--out",
        type=Path,
        default=WORKING_DIR / "ingested.csv",
        help="Output CSV path (default: artifacts/working/ingested.csv).",
    )
    args = parser.parse_args(argv)

    records = list(cycle_records(args.limit))
    written = write_csv(records, args.out)
    log_event("ingest", f"Generated {written} raw records.", extra={"output": str(args.out)})
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
