"""Classification step mapping normalized rows to taxonomy buckets."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import List

from scripts.python.classify_products_v2 import classify, norm_brand, up

from . import WORKING_DIR, ensure_directories, log_event


def classify_file(input_path: Path, output_path: Path) -> int:
    ensure_directories()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with input_path.open("r", newline="", encoding="utf-8") as src, output_path.open(
        "w", newline="", encoding="utf-8"
    ) as dst:
        reader = csv.DictReader(src)
        fieldnames = reader.fieldnames or []
        if "family" not in fieldnames:
            fieldnames.append("family")
        if "subfamily" not in fieldnames:
            fieldnames.append("subfamily")
        writer = csv.DictWriter(dst, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            row["brand"] = norm_brand(row.get("brand", ""))
            fam, sub = classify(
                up(row.get("name", "")),
                up(row.get("category_raw", "")),
                up(row.get("country", "")),
            )
            row["family"], row["subfamily"] = fam, sub
            writer.writerow(row)
            count += 1
    return count


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assign families/subfamilies to normalized rows.")
    parser.add_argument(
        "--in",
        dest="input_path",
        type=Path,
        default=WORKING_DIR / "normalized.csv",
        help="Input CSV from the normalize step.",
    )
    parser.add_argument(
        "--out",
        dest="output_path",
        type=Path,
        default=WORKING_DIR / "classified.csv",
        help="Output CSV path (default: artifacts/working/classified.csv).",
    )
    args = parser.parse_args(argv)

    count = classify_file(args.input_path, args.output_path)
    log_event("classify", f"Classified {count} rows.", extra={"output": str(args.output_path)})
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
