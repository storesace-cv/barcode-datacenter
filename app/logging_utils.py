"""Utilities for configuring comprehensive application logging."""

from __future__ import annotations

import atexit
import io
import logging
import os
import sys
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import TextIO

_LOG_INITIALIZED = False
_LOG_LOCK = threading.Lock()
_ORIGINAL_STDOUT: TextIO | None = None
_ORIGINAL_STDERR: TextIO | None = None


class _TeeStream(io.TextIOBase):
    """Duplicate stream writes to the original stream and the log file."""

    def __init__(self, original: TextIO, log_file: Path, label: str) -> None:
        self._original = original
        self._log_file_path = log_file
        self._label = label
        self._buffer = ""
        self._lock = threading.Lock()

    def write(self, s: str) -> int:  # type: ignore[override]
        if not s:
            return 0
        with self._lock:
            self._original.write(s)
            self._original.flush()
            self._buffer += s.replace("\r\n", "\n").replace("\r", "\n")
            lines = self._buffer.split("\n")
            self._buffer = lines.pop()  # keep trailing partial line
            if lines:
                with open(self._log_file_path, "a", encoding="utf-8") as handle:
                    for line in lines:
                        if not line and not self._label:
                            continue
                        timestamp = datetime.now(timezone.utc).isoformat()
                        handle.write(f"{timestamp} [{self._label}] {line}\n")
        return len(s)

    def flush(self) -> None:  # type: ignore[override]
        with self._lock:
            self._original.flush()
            if self._buffer:
                with open(self._log_file_path, "a", encoding="utf-8") as handle:
                    timestamp = datetime.now(timezone.utc).isoformat()
                    handle.write(f"{timestamp} [{self._label}] {self._buffer}\n")
                self._buffer = ""

    def fileno(self) -> int:  # type: ignore[override]
        return self._original.fileno()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _log_path() -> Path:
    return _repo_root() / "logs" / "app_full_logs.txt"


def _ensure_logfile() -> Path:
    log_path = _log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    return log_path


def _write_session_header(logger: logging.Logger, log_file: Path) -> None:
    header_lines = [
        "=" * 80,
        "Barcode Datacenter – full application logging enabled",
        f"Started at: {datetime.now(timezone.utc).isoformat()}",
        f"Command: {' '.join(sys.argv)}",
        f"Working directory: {Path.cwd()}",
    ]
    for line in header_lines:
        logger.info(line)
    # Persist header in plain text for streams as well.
    with open(log_file, "a", encoding="utf-8") as handle:
        for line in header_lines:
            handle.write(f"{line}\n")


def _install_exception_hook(logger: logging.Logger) -> None:
    def _hook(exc_type, exc_value, exc_traceback):  # type: ignore[override]
        if issubclass(exc_type, KeyboardInterrupt):
            logger.info("KeyboardInterrupt received", exc_info=(exc_type, exc_value, exc_traceback))
        else:
            logger.critical(
                "Uncaught exception",
                exc_info=(exc_type, exc_value, exc_traceback),
            )
        assert _ORIGINAL_STDERR is not None
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=_ORIGINAL_STDERR)

    sys.excepthook = _hook  # type: ignore[assignment]


def _install_stream_tees(log_file: Path) -> None:
    global _ORIGINAL_STDOUT, _ORIGINAL_STDERR
    if _ORIGINAL_STDOUT is None:
        _ORIGINAL_STDOUT = sys.stdout
    if _ORIGINAL_STDERR is None:
        _ORIGINAL_STDERR = sys.stderr

    sys.stdout = _TeeStream(_ORIGINAL_STDOUT, log_file, "STDOUT")  # type: ignore[assignment]
    sys.stderr = _TeeStream(_ORIGINAL_STDERR, log_file, "STDERR")  # type: ignore[assignment]


def _setup_logging_handlers(log_file: Path) -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s (%(process)d:%(threadName)s) - %(message)s"
    )
    file_handler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(file_handler)
    logging.captureWarnings(True)
    return logger


def _register_shutdown_hook(logger: logging.Logger, log_file: Path) -> None:
    def _shutdown() -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        logger.info("Shutting down application logging at %s", timestamp)
        if logger.handlers:
            for handler in list(logger.handlers):
                handler.flush()
        with open(log_file, "a", encoding="utf-8") as handle:
            handle.write(f"Session closed at {timestamp}\n")

    atexit.register(_shutdown)


def initialize_logging_if_requested() -> None:
    """Enable exhaustive logging if the debug flag is present."""

    global _LOG_INITIALIZED

    flag = os.environ.get("APP_FULL_LOGGING", "").strip().lower()
    if flag not in {"1", "true", "yes", "on"}:
        return

    if _LOG_INITIALIZED:
        return

    with _LOG_LOCK:
        if _LOG_INITIALIZED:
            return

        log_file = _ensure_logfile()
        logger = _setup_logging_handlers(log_file)
        _install_stream_tees(log_file)
        _install_exception_hook(logger)
        _register_shutdown_hook(logger, log_file)
        _write_session_header(logger, log_file)
        logger.debug("Environment variables snapshot: %s", dict(os.environ))
        _LOG_INITIALIZED = True


__all__ = ["initialize_logging_if_requested"]
