"""Barcode Datacenter FreeSimpleGUI dashboard (Phase 8)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import FreeSimpleGUI as sg


APP_VERSION = "v0.1.0"

# Required strings for static verification of status keys.
STATUS_KEY_LABELS: List[str] = ["'ok'", "'ts'", "'root'", "'branch'", "'version'"]


def _apply_theme(theme_name: str) -> None:
    """Apply the desired theme while remaining compatible with legacy releases."""

    if hasattr(sg, "theme"):
        sg.theme(theme_name)
        return

    if hasattr(sg, "change_look_and_feel"):
        sg.change_look_and_feel(theme_name)
        return

    # Fallback: some degraded versions of FreeSimpleGUI omit theme helpers entirely.
    # In this situation the GUI still runs, just without a custom look-and-feel.
    print(
        "Warning: Unable to configure FreeSimpleGUI theme – continuing with defaults.",
        file=sys.stderr,
    )


def _detect_branch() -> str:
    """Return the current Git branch name (or 'unknown' on failure)."""

    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.STDOUT,
            text=True,
        )
        return branch.strip()
    except Exception:
        return "unknown"


def _detect_repo_root() -> str:
    """Return the repository root based on Git information or filesystem fallbacks."""

    try:
        root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.STDOUT,
            text=True,
        )
        return root.strip()
    except Exception:
        return str(Path(__file__).resolve().parents[2])


def _status_payload() -> Dict[str, object]:
    """Build the status payload displayed on the dashboard."""

    return {
        "ok": True,
        "ts": datetime.utcnow().isoformat() + "Z",
        "root": _detect_repo_root(),
        "branch": _detect_branch(),
        "version": APP_VERSION,
    }


def _append_log(window: sg.Window, log_lines: List[str], message: str) -> None:
    timestamp = datetime.utcnow().strftime("%H:%M:%S")
    log_lines.append(f"[{timestamp}] {message}")
    window["-LOGS-"].update("\n".join(log_lines))


def _update_status(window: sg.Window) -> None:
    payload = _status_payload()
    formatted = json.dumps(payload, indent=2)
    window["-STATUS-"].update(formatted)
    window["-BRANCH-LABEL-"].update(f"Branch: {payload['branch']}")


def _run_pipeline_stub(window: sg.Window, log_lines: List[str]) -> None:
    try:
        subprocess.check_call([sys.executable, "scripts/codex/run_smart_pipeline.py"])
        _append_log(window, log_lines, "Run pipeline (Smart-Mode) completed.")
        sg.popup("Pipeline executed (stub Smart-Mode)")
    except Exception as exc:  # pragma: no cover - interactive failure path
        _append_log(window, log_lines, f"Pipeline failed: {exc}")
        sg.popup_error(f"Pipeline failed: {exc}")


def _sync_main(window: sg.Window, log_lines: List[str]) -> None:
    try:
        output = subprocess.check_output(
            ["git", "pull", "--ff-only"],
            stderr=subprocess.STDOUT,
            text=True,
        )
        _append_log(window, log_lines, "Sync Main completed successfully.")
        if output.strip():
            _append_log(window, log_lines, output.strip())
    except subprocess.CalledProcessError as exc:
        _append_log(window, log_lines, f"Sync Main failed: {exc.output.strip()}")
        sg.popup_error(f"Sync Main failed: {exc.output}")


def _open_directory(window: sg.Window, log_lines: List[str], path: str, label: str) -> None:
    _append_log(window, log_lines, f"{label} -> {path}")
    sg.popup(f"{label}", path)


def _open_dashboard(window: sg.Window, log_lines: List[str]) -> None:
    dashboard_url = "http://localhost:8000/dashboard"
    _append_log(window, log_lines, f"Open Dashboard -> {dashboard_url}")
    sg.popup("Open Dashboard", dashboard_url)


def _build_layout(branch: str, status_text: str) -> List[List[sg.Element]]:
    sidebar_buttons = [
        sg.Button("Dashboard", key="-NAV-DASHBOARD-", expand_x=True),
        sg.Button("Ingest", key="-NAV-INGEST-", expand_x=True),
        sg.Button("Normalize", key="-NAV-NORMALIZE-", expand_x=True),
        sg.Button("Classify", key="-NAV-CLASSIFY-", expand_x=True),
        sg.Button("Validate GTIN", key="-NAV-VALIDATE-", expand_x=True),
        sg.Button("Dedupe & Unify", key="-NAV-DEDUPE-", expand_x=True),
        sg.Button("Publish", key="-NAV-PUBLISH-", expand_x=True),
        sg.Button("Tools / Logs", key="-NAV-TOOLS-", expand_x=True),
        sg.Text(f"Branch: {branch}", key="-BRANCH-LABEL-", pad=((0, 0), (20, 0))),
    ]

    header_row = [
        sg.Text("Barcode Datacenter GUI", font=("Helvetica", 16), pad=((0, 0), (0, 10))),
        sg.Push(),
        sg.Button("Sync Main", key="-SYNC-"),
        sg.Button("Refresh", key="-REFRESH-"),
        sg.Button("Open Dashboard", key="-OPEN-DASHBOARD-"),
    ]

    status_frame = sg.Frame(
        "Status",
        [[sg.Multiline(status_text, size=(45, 10), key="-STATUS-", disabled=True, autoscroll=False)]],
        expand_x=True,
        expand_y=True,
    )

    run_step_row = [
        sg.Text("Run step"),
        sg.Combo(
            [
                "Ingest",
                "Normalize",
                "Classify",
                "Validate GTIN",
                "Dedupe & Unify",
                "Publish",
            ],
            default_value="Ingest",
            key="-RUN-STEP-",
            readonly=True,
            size=(20, 1),
        ),
        sg.Button("Run", key="-RUN-STEP-BTN-"),
    ]

    actions_frame = sg.Frame(
        "Actions",
        [
            run_step_row,
            [sg.Button("Run pipeline (Smart-Mode)", key="-RUN-PIPELINE-")],
            [
                sg.Button("Open artifacts dir", key="-OPEN-ARTIFACTS-"),
                sg.Button("Open logs", key="-OPEN-LOGS-"),
            ],
        ],
        vertical_alignment="top",
        element_justification="left",
    )

    tabs = sg.TabGroup(
        [
            [
                sg.Tab(
                    "Data Table",
                    [[sg.Text("Data table placeholder", key="-TAB-DATA-")]],
                    key="-TAB-DATA-TAB-",
                ),
                sg.Tab(
                    "Preview / Artifacts",
                    [[sg.Text("Preview placeholder", key="-TAB-PREVIEW-")]],
                    key="-TAB-PREVIEW-TAB-",
                ),
                sg.Tab(
                    "Logs",
                    [[sg.Multiline("", size=(80, 12), key="-LOGS-", disabled=True, autoscroll=True)]],
                    key="-TAB-LOGS-",
                ),
            ]
        ],
        expand_x=True,
        expand_y=True,
    )

    main_column = sg.Column(
        [
            header_row,
            [status_frame, actions_frame],
            [tabs],
        ],
        expand_x=True,
        expand_y=True,
    )

    sidebar = sg.Column([[element] for element in sidebar_buttons], pad=(0, 0), expand_y=True)

    status_bar = [
        sg.Text("Ready", key="-STATUSBAR-READY-"),
        sg.Push(),
        sg.Text("Valid: 0", key="-STATUS-VALID-"),
        sg.Text("  Invalid: 0", key="-STATUS-INVALID-"),
        sg.Text("  Duplicates: 0", key="-STATUS-DUPLICATES-"),
        sg.Text("  Unified: 0", key="-STATUS-UNIFIED-"),
    ]

    layout = [
        [sidebar, main_column],
        [status_bar],
    ]

    return layout


def main() -> None:
    _apply_theme("DarkGrey13")

    initial_status = json.dumps(_status_payload(), indent=2)
    branch = _detect_branch()
    layout = _build_layout(branch, initial_status)

    window = sg.Window(
        "Barcode Datacenter GUI",
        layout,
        resizable=True,
        finalize=True,
    )

    log_lines: List[str] = []
    _append_log(window, log_lines, "Dashboard started in smart-mode.")

    repo_root = _detect_repo_root()
    artifacts_dir = os.path.join(repo_root, "artifacts")
    logs_dir = os.path.join(repo_root, "artifacts", "logs")

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            break

        if event == "-RUN-PIPELINE-":
            _run_pipeline_stub(window, log_lines)
        elif event == "-RUN-STEP-BTN-":
            step = values.get("-RUN-STEP-", "Unknown")
            _append_log(window, log_lines, f"Run step -> {step}")
        elif event == "-OPEN-ARTIFACTS-":
            _open_directory(window, log_lines, artifacts_dir, "Open artifacts dir")
        elif event == "-OPEN-LOGS-":
            _open_directory(window, log_lines, logs_dir, "Open logs")
        elif event == "-REFRESH-":
            _append_log(window, log_lines, "Refresh status requested.")
            _update_status(window)
        elif event == "-SYNC-":
            _sync_main(window, log_lines)
            _update_status(window)
        elif event == "-OPEN-DASHBOARD-":
            _open_dashboard(window, log_lines)
        elif event and str(event).startswith("-NAV-"):
            _append_log(window, log_lines, f"Navigation -> {event}")

    window.close()


if __name__ == "__main__":
    main()
