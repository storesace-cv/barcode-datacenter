from __future__ import annotations

import csv
import json
import sqlite3

from pipeline import OUTPUTS_DIR, PHASE9_LOG, WORKING_DIR
from pipeline.run import main as pipeline_main


ARTIFACT_FILES = [
    WORKING_DIR / "ingested.csv",
    WORKING_DIR / "normalized.csv",
    WORKING_DIR / "classified.csv",
    WORKING_DIR / "validated.csv",
    WORKING_DIR / "unified.csv",
    WORKING_DIR / "duplicates.csv",
    OUTPUTS_DIR / "final.csv",
    OUTPUTS_DIR / "final.jsonl",
    OUTPUTS_DIR / "final.sqlite",
    PHASE9_LOG,
]


def _cleanup() -> None:
    for path in ARTIFACT_FILES:
        if path.exists():
            path.unlink()


def test_pipeline_creates_final_artifacts(tmp_path):
    _cleanup()

    pipeline_main(["--limit", "6", "--country", "PT"])

    final_csv = OUTPUTS_DIR / "final.csv"
    final_sqlite = OUTPUTS_DIR / "final.sqlite"

    assert final_csv.exists()
    assert final_sqlite.exists()

    with final_csv.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows, "Final CSV should contain data"

    # SQLite should hold the same number of rows
    conn = sqlite3.connect(final_sqlite)
    try:
        cur = conn.execute("SELECT COUNT(*) FROM products")
        (count,) = cur.fetchone()
    finally:
        conn.close()
    assert count == len(rows)

    # The pipeline log should include the pipeline completion entry
    assert PHASE9_LOG.exists()
    with PHASE9_LOG.open(encoding="utf-8") as fh:
        entries = [json.loads(line) for line in fh if line.strip()]
    assert any(entry.get("step") == "pipeline" for entry in entries)
