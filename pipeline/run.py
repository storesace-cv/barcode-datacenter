"""Convenience runner executing the full smart-mode pipeline end-to-end."""

from __future__ import annotations

import argparse
from typing import List

from . import WORKING_DIR, log_event
from . import ensure_directories
from . import OUTPUTS_DIR
from .ingest import main as ingest_main
from .normalize import main as normalize_main
from .classify import main as classify_main
from .validate import main as validate_main
from .dedupe import main as dedupe_main
from .publish import main as publish_main


def run_all(limit: int, country: str) -> None:
    ensure_directories()
    ingest_main(["--limit", str(limit), "--out", str(WORKING_DIR / "ingested.csv")])
    normalize_main(
        [
            "--in",
            str(WORKING_DIR / "ingested.csv"),
            "--out",
            str(WORKING_DIR / "normalized.csv"),
            "--country",
            country,
        ]
    )
    classify_main(["--in", str(WORKING_DIR / "normalized.csv"), "--out", str(WORKING_DIR / "classified.csv")])
    validate_main(["--in", str(WORKING_DIR / "classified.csv"), "--out", str(WORKING_DIR / "validated.csv")])
    dedupe_main(
        [
            "--in",
            str(WORKING_DIR / "validated.csv"),
            "--out",
            str(WORKING_DIR / "unified.csv"),
            "--dup-report",
            str(WORKING_DIR / "duplicates.csv"),
        ]
    )
    publish_main(["--in", str(WORKING_DIR / "unified.csv"), "--outdir", str(OUTPUTS_DIR)])


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the complete pipeline end-to-end.")
    parser.add_argument("--limit", type=int, default=50, help="Number of ingestion records to generate.")
    parser.add_argument("--country", default="PT", help="Country code used during normalization/classification.")
    args = parser.parse_args(argv)

    run_all(args.limit, args.country.upper())
    log_event(
        "pipeline",
        "Pipeline completed successfully.",
        extra={
            "ingested": str(WORKING_DIR / "ingested.csv"),
            "final_csv": str(OUTPUTS_DIR / "final.csv"),
        },
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
