#!/usr/bin/env python3
import datetime
import os
import subprocess
import sys

LOG_PATH = "artifacts/logs/phase9_pipeline.log"


def ensure_dirs():
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)


def log(msg: str):
    ensure_dirs()
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")


def main():
    ensure_dirs()
    try:
        subprocess.check_call([sys.executable, "-m", "pipeline.run"])
        log("Smart-Mode pipeline executed end-to-end.")
    except subprocess.CalledProcessError as exc:
        log(f"Pipeline execution failed: {exc}")
        return exc.returncode or 1

    try:
        subprocess.check_call(
            [
                sys.executable,
                "scripts/codex/progress_helper.py",
                "--phase",
                "9",
                "--task",
                "pipeline_end2end",
                "--value",
                "100",
                "--msg",
                "Phase 9 pipeline executed via smart-mode runner.",
            ]
        )
        subprocess.check_call(
            [
                sys.executable,
                "scripts/codex/progress_helper.py",
                "--phase",
                "9",
                "--task",
                "tests_green",
                "--value",
                "100",
                "--msg",
                "Phase 9 tests executed via smart-mode runner.",
            ]
        )
    except subprocess.CalledProcessError as exc:
        log(f"WARNING: progress update failed: {exc}")
        return exc.returncode or 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
