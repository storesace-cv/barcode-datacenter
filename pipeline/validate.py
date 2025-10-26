"""Validate GTIN codes for the smart-mode pipeline."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import List

from scripts.python.validate_gtin import valid_gtin

from . import WORKING_DIR, ensure_directories, log_event
from .models import StepResult


def validate_file(input_path: Path, output_path: Path) -> int:
    ensure_directories()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with input_path.open("r", newline="", encoding="utf-8") as src, output_path.open(
        "w", newline="", encoding="utf-8"
    ) as dst:
        reader = csv.DictReader(src)
        fieldnames = list(reader.fieldnames or [])
        if "gtin_valid" not in fieldnames:
            fieldnames.append("gtin_valid")
        writer = csv.DictWriter(dst, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            gtin = (row.get("gtin") or "").strip()
            row["gtin_valid"] = "1" if gtin and valid_gtin(gtin) else "0"
            writer.writerow(row)
            count += 1
    return count


def run_validate(
    input_path: Path = WORKING_DIR / "classified.csv",
    output_path: Path = WORKING_DIR / "validated.csv",
) -> StepResult:
    count = validate_file(input_path, output_path)
    result = StepResult(
        name="validate",
        status="ok" if count else "empty",
        metrics={"validated": count},
        artifacts={"csv": str(output_path)},
    )
    log_event("validate", f"Validated {count} rows.", extra=result.metrics)
    return result


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate GTIN codes and add gtin_valid column.")
    parser.add_argument(
        "--in",
        dest="input_path",
        type=Path,
        default=WORKING_DIR / "classified.csv",
        help="Input CSV from the classify step.",
    )
    parser.add_argument(
        "--out",
        dest="output_path",
        type=Path,
        default=WORKING_DIR / "validated.csv",
        help="Output CSV path (default: artifacts/working/validated.csv).",
    )
    args = parser.parse_args(argv)

    run_validate(args.input_path, args.output_path)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
