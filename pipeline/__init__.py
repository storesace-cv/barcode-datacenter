"""Pipeline utilities and shared constants for the Barcode Datacenter app."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
import json
import os

REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_ROOT = REPO_ROOT / "artifacts"
INPUTS_DIR = ARTIFACTS_ROOT / "inputs"
WORKING_DIR = ARTIFACTS_ROOT / "working"
OUTPUTS_DIR = ARTIFACTS_ROOT / "outputs"
LOGS_DIR = ARTIFACTS_ROOT / "logs"
PHASE9_LOG = LOGS_DIR / "phase9_pipeline.log"
GUI_LOG = LOGS_DIR / "gui_actions.log"

SMART_MODE = True


def ensure_directories() -> None:
    """Ensure that the required artifacts folders exist."""

    for path in (INPUTS_DIR, WORKING_DIR, OUTPUTS_DIR, LOGS_DIR):
        path.mkdir(parents=True, exist_ok=True)


@dataclass
class LogRecord:
    step: str
    message: str
    status: str = "info"
    extra: Dict[str, Any] | None = None

    def to_json(self) -> str:
        payload: Dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "step": self.step,
            "status": self.status,
            "message": self.message,
        }
        if self.extra:
            payload.update(self.extra)
        return json.dumps(payload, ensure_ascii=False)


def log_event(step: str, message: str, *, status: str = "info", extra: Dict[str, Any] | None = None) -> None:
    """Append a structured log entry to the Phase 9 pipeline log."""

    ensure_directories()
    record = LogRecord(step=step, message=message, status=status, extra=extra)
    with open(PHASE9_LOG, "a", encoding="utf-8") as fh:
        fh.write(record.to_json() + os.linesep)
    # Mirror to stdout for CLI friendliness.
    print(f"[{status.upper()}] {step}: {message}")


__all__ = [
    "ARTIFACTS_ROOT",
    "INPUTS_DIR",
    "WORKING_DIR",
    "OUTPUTS_DIR",
    "LOGS_DIR",
    "PHASE9_LOG",
    "GUI_LOG",
    "SMART_MODE",
    "ensure_directories",
    "log_event",
]
