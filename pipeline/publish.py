"""Publish step exporting the unified dataset to final artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from pathlib import Path
from typing import List

from . import OUTPUTS_DIR, ensure_directories, log_event

FINAL_CSV = "final.csv"
FINAL_JSONL = "final.jsonl"
FINAL_SQLITE = "final.sqlite"


def load_rows(unified_path: Path) -> List[dict]:
    with unified_path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    return rows


def export_csv(rows: List[dict], columns: List[str], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def export_jsonl(rows: List[dict], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def export_sqlite(rows: List[dict], columns: List[str], output_path: Path) -> None:
    conn = sqlite3.connect(output_path)
    try:
        col_defs = ", ".join(f'"{col}" TEXT' for col in columns)
        conn.execute(f"CREATE TABLE IF NOT EXISTS products ({col_defs});")
        conn.execute("DELETE FROM products;")
        if rows:
            placeholders = ", ".join(["?"] * len(columns))
            conn.executemany(
                f"INSERT INTO products ({', '.join(columns)}) VALUES ({placeholders});",
                [[row.get(col, "") for col in columns] for row in rows],
            )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_products_gtin ON products(gtin);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_products_family ON products(family, subfamily);")
        conn.commit()
    finally:
        conn.close()


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Publish the unified dataset to CSV/JSONL/SQLite artifacts.")
    parser.add_argument(
        "--in",
        dest="input_path",
        type=Path,
        default=Path("artifacts/working/unified.csv"),
        help="Unified CSV input path.",
    )
    parser.add_argument(
        "--outdir",
        dest="output_dir",
        type=Path,
        default=OUTPUTS_DIR,
        help="Output directory for final artifacts.",
    )
    args = parser.parse_args(argv)

    ensure_directories()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows = load_rows(args.input_path)
    columns = list(rows[0].keys()) if rows else []

    csv_path = args.output_dir / FINAL_CSV
    jsonl_path = args.output_dir / FINAL_JSONL
    sqlite_path = args.output_dir / FINAL_SQLITE

    export_csv(rows, columns, csv_path)
    export_jsonl(rows, jsonl_path)
    export_sqlite(rows, columns, sqlite_path)

    log_event(
        "publish",
        f"Published {len(rows)} rows to final artifacts.",
        extra={
            "csv": str(csv_path),
            "jsonl": str(jsonl_path),
            "sqlite": str(sqlite_path),
        },
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
