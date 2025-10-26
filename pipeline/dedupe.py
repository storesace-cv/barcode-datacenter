"""Dedupe & unify step for the smart-mode pipeline."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple

from scripts.python.dedupe_unify import make_key

from . import WORKING_DIR, ensure_directories, log_event

ORDERED_FIELDS = [
    "gtin",
    "gtin_valid",
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
    "provenance",
]


def unify_rows(input_path: Path) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    with input_path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    unified: Dict[Tuple[str, str], Dict[str, str]] = {}
    duplicates: List[Dict[str, str]] = []

    for row in rows:
        key = make_key(row)
        base = unified.get(key)
        if base is None:
            provenance = row.get("source", "UNKNOWN") or "UNKNOWN"
            base = dict(row)
            base["provenance"] = json.dumps([provenance])
            unified[key] = base
        else:
            for field, value in row.items():
                if not base.get(field) and value:
                    base[field] = value
            provenance = row.get("source", "UNKNOWN") or "UNKNOWN"
            prov_list = json.loads(base.get("provenance", "[]"))
            if provenance not in prov_list:
                prov_list.append(provenance)
            base["provenance"] = json.dumps(sorted(set(prov_list)))
            duplicates.append(
                {
                    "key_type": key[0],
                    "key": key[1],
                    "gtin": row.get("gtin", ""),
                    "name": row.get("name", ""),
                    "source": provenance,
                }
            )

    return list(unified.values()), duplicates


def write_outputs(unified_rows: List[Dict[str, str]], duplicates: List[Dict[str, str]], unified_path: Path, report_path: Path) -> None:
    ensure_directories()
    unified_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = ORDERED_FIELDS[:]
    for row in unified_rows:
        for column in row.keys():
            if column not in fieldnames:
                fieldnames.append(column)

    with unified_path.open("w", newline="", encoding="utf-8") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        for row in unified_rows:
            writer.writerow(row)

    with report_path.open("w", newline="", encoding="utf-8") as freport:
        report_fields = ["key_type", "key", "gtin", "name", "source"]
        writer = csv.DictWriter(freport, fieldnames=report_fields)
        writer.writeheader()
        for dup in duplicates:
            writer.writerow(dup)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Dedupe validated rows and build a unified dataset.")
    parser.add_argument(
        "--in",
        dest="input_path",
        type=Path,
        default=WORKING_DIR / "validated.csv",
        help="Input CSV from the validate step.",
    )
    parser.add_argument(
        "--out",
        dest="output_path",
        type=Path,
        default=WORKING_DIR / "unified.csv",
        help="Unified CSV path (default: artifacts/working/unified.csv).",
    )
    parser.add_argument(
        "--dup-report",
        dest="dup_report",
        type=Path,
        default=WORKING_DIR / "duplicates.csv",
        help="Duplicates report path (default: artifacts/working/duplicates.csv).",
    )
    args = parser.parse_args(argv)

    unified_rows, duplicates = unify_rows(args.input_path)
    write_outputs(unified_rows, duplicates, args.output_path, args.dup_report)
    log_event(
        "dedupe",
        f"Unified {len(unified_rows)} records (duplicates: {len(duplicates)}).",
        extra={"output": str(args.output_path), "duplicates": str(args.dup_report)},
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
