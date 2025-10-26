"""Convenience runner executing the full smart-mode pipeline end-to-end."""

from __future__ import annotations

import argparse
from typing import List, Sequence

from . import OUTPUTS_DIR, WORKING_DIR, log_event
from .orchestrator import SmartPipelineRunner


def run_all(limit: int, countries: Sequence[str], offline: bool = False) -> None:
    runner = SmartPipelineRunner()
    overrides = {
        "ingest": {
            "limit": limit,
            "countries": tuple(c.upper() for c in countries),
            "prefer_online": False if offline else None,
        }
    }
    runner.run_all(overrides=overrides)
    log_event(
        "pipeline",
        "Pipeline completed successfully.",
        extra={
            "ingested": str(WORKING_DIR / "ingested.csv"),
            "final_csv": str(OUTPUTS_DIR / "final.csv"),
        },
    )


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the complete pipeline end-to-end.")
    parser.add_argument("--limit", type=int, default=120, help="Maximum number of unique ingestion records.")
    parser.add_argument(
        "--country",
        dest="countries",
        action="append",
        default=["PT", "ANG", "CV"],
        help="Countries to include during ingestion (repeat for multiples).",
    )
    parser.add_argument("--offline", action="store_true", help="Disable online fetching during ingestion.")
    args = parser.parse_args(argv)

    run_all(args.limit, [c.upper() for c in args.countries], offline=args.offline)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
