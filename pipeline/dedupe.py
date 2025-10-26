"""Deduplicate validated rows using connector-aware scoring."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple

from scripts.python.dedupe_unify import make_key

from . import WORKING_DIR, ensure_directories, log_event
from .models import StepResult

ORDERED_FIELDS = [
    "gtin",
    "gtin_valid",
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


def _score_row(row: Dict[str, str]) -> Tuple[int, float, bool]:
    priority = int(row.get("priority") or 0)
    confidence = float(row.get("confidence") or 0.0)
    source_type = row.get("source_type", "")
    gtin_valid = row.get("gtin_valid") == "1"
    price_present = bool(row.get("price_amount"))

    base = priority
    if source_type == "supermarket":
        base += 40
    elif source_type == "open-data":
        base += 10
    if gtin_valid:
        base += 5
    if price_present:
        base += 2
    return base, confidence, price_present


def _merge_provenance(base_row: Dict[str, str], new_row: Dict[str, str]) -> None:
    base_prov = json.loads(base_row.get("provenance", "[]") or "[]")
    new_prov = json.loads(new_row.get("provenance", "[]") or "[]")
    seen = {json.dumps(entry, sort_keys=True) for entry in base_prov}
    for entry in new_prov:
        key = json.dumps(entry, sort_keys=True)
        if key not in seen:
            base_prov.append(entry)
            seen.add(key)
    base_row["provenance"] = json.dumps(base_prov, ensure_ascii=False)


def _merge_rows(base_row: Dict[str, str], new_row: Dict[str, str]) -> Dict[str, str]:
    base_score = _score_row(base_row)
    new_score = _score_row(new_row)

    if new_score > base_score:
        base_row, new_row = new_row, base_row

    for field, value in new_row.items():
        if not value:
            continue
        if not base_row.get(field):
            base_row[field] = value

    _merge_provenance(base_row, new_row)
    return base_row


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
            unified[key] = dict(row)
        else:
            merged = _merge_rows(base, dict(row))
            unified[key] = merged
            duplicates.append(
                {
                    "key_type": key[0],
                    "key": key[1],
                    "gtin": row.get("gtin", ""),
                    "name": row.get("name", ""),
                    "source": row.get("source", ""),
                    "source_type": row.get("source_type", ""),
                }
            )

    return list(unified.values()), duplicates


def run_dedupe(
    input_path: Path = WORKING_DIR / "validated.csv",
    output_path: Path = WORKING_DIR / "unified.csv",
    report_path: Path = WORKING_DIR / "duplicates.csv",
) -> StepResult:
    unified_rows, duplicates = unify_rows(input_path)
    write_outputs(unified_rows, duplicates, output_path, report_path)
    result = StepResult(
        name="dedupe",
        status="ok",
        metrics={"unified": len(unified_rows), "duplicates": len(duplicates)},
        artifacts={"unified_csv": str(output_path), "duplicates_csv": str(report_path)},
    )
    log_event(
        "dedupe",
        f"Unified {len(unified_rows)} records (duplicates: {len(duplicates)}).",
        extra=result.metrics,
    )
    return result


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
        report_fields = ["key_type", "key", "gtin", "name", "source", "source_type"]
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

    run_dedupe(args.input_path, args.output_path, args.dup_report)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
