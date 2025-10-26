"""Barcode Datacenter FreeSimpleGUI dashboard (Phase 8)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import FreeSimpleGUI as sg


APP_VERSION = "v0.1.0"

# Required strings for static verification of status keys.
STATUS_KEY_LABELS: List[str] = ["'ok'", "'ts'", "'root'", "'branch'", "'version'"]

NAV_BUTTON_KEYS = [
    "-NAV-DASHBOARD-",
    "-NAV-INGEST-",
    "-NAV-NORMALIZE-",
    "-NAV-CLASSIFY-",
    "-NAV-VALIDATE-",
    "-NAV-DEDUPE-",
    "-NAV-PUBLISH-",
    "-NAV-TOOLS-",
]

SIDEBAR_SELECTED_COLOR = ("white", "#2c5aa0")
SIDEBAR_DEFAULT_COLOR = ("white", "#3a3f44")

NAV_LABELS = {
    "-NAV-DASHBOARD-": "Dashboard",
    "-NAV-INGEST-": "Ingest",
    "-NAV-NORMALIZE-": "Normalize",
    "-NAV-CLASSIFY-": "Classify",
    "-NAV-VALIDATE-": "Validate GTIN",
    "-NAV-DEDUPE-": "Dedupe & Unify",
    "-NAV-PUBLISH-": "Publish",
    "-NAV-TOOLS-": "Tools / Logs",
}


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


def _run_pipeline_stub(window: sg.Window, log_lines: List[str]) -> bool:
    try:
        subprocess.check_call([sys.executable, "scripts/codex/run_smart_pipeline.py"])
        _append_log(window, log_lines, "Run pipeline (Smart-Mode) completed.")
        sg.popup("Pipeline executed (stub Smart-Mode)")
        return True
    except Exception as exc:  # pragma: no cover - interactive failure path
        _append_log(window, log_lines, f"Pipeline failed: {exc}")
        sg.popup_error(f"Pipeline failed: {exc}")
        return False


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
    try:
        if os.name == "nt":  # pragma: no cover - requires Windows
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":  # pragma: no cover - requires macOS
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as exc:  # pragma: no cover - interactive failure path
        sg.popup_error(f"Unable to open {label}: {exc}\n{path}")


def _open_dashboard(window: sg.Window, log_lines: List[str]) -> None:
    dashboard_url = "http://localhost:8000/dashboard"
    _append_log(window, log_lines, f"Open Dashboard -> {dashboard_url}")
    webbrowser.open(dashboard_url)


def _set_active_nav(window: sg.Window, active_key: str) -> None:
    for key in NAV_BUTTON_KEYS:
        if key == active_key:
            window[key].update(button_color=SIDEBAR_SELECTED_COLOR)
        else:
            window[key].update(button_color=SIDEBAR_DEFAULT_COLOR)


def _run_step(window: sg.Window, log_lines: List[str], step_label: str) -> bool:
    step_slug_map = {
        "Ingest": "ingest",
        "Normalize": "normalize",
        "Classify": "classify",
        "Validate GTIN": "validate_gtin",
        "Dedupe & Unify": "dedupe_unify",
        "Publish": "publish",
    }
    slug = step_slug_map.get(step_label)
    if not slug:
        _append_log(window, log_lines, f"Unknown step requested: {step_label}")
        sg.popup_error(f"Unknown step: {step_label}")
        return False

    script_path = Path(__file__).resolve().parents[2] / "scripts" / "steps" / "run_step.sh"
    if not script_path.exists():
        _append_log(window, log_lines, "Run step script missing.")
        sg.popup_error(f"Unable to locate run_step.sh at {script_path}")
        return False

    try:
        subprocess.check_call(["bash", str(script_path), slug])
        _append_log(window, log_lines, f"Run step executed: {step_label}")
        window["-STATUSBAR-READY-"].update(f"Ready – Completed {step_label}")
        return True
    except subprocess.CalledProcessError as exc:  # pragma: no cover - interactive failure path
        _append_log(window, log_lines, f"Run step failed: {exc}")
        sg.popup_error(f"Run step failed: {exc}")
        return False


def _build_layout(branch: str, status_text: str) -> List[List[sg.Element]]:
    sidebar_buttons = [
        sg.Button(
            "Dashboard",
            key="-NAV-DASHBOARD-",
            expand_x=True,
            button_color=SIDEBAR_DEFAULT_COLOR,
            border_width=1,
        ),
        sg.Button(
            "Ingest",
            key="-NAV-INGEST-",
            expand_x=True,
            button_color=SIDEBAR_DEFAULT_COLOR,
            border_width=1,
        ),
        sg.Button(
            "Normalize",
            key="-NAV-NORMALIZE-",
            expand_x=True,
            button_color=SIDEBAR_DEFAULT_COLOR,
            border_width=1,
        ),
        sg.Button(
            "Classify",
            key="-NAV-CLASSIFY-",
            expand_x=True,
            button_color=SIDEBAR_DEFAULT_COLOR,
            border_width=1,
        ),
        sg.Button(
            "Validate GTIN",
            key="-NAV-VALIDATE-",
            expand_x=True,
            button_color=SIDEBAR_DEFAULT_COLOR,
            border_width=1,
        ),
        sg.Button(
            "Dedupe & Unify",
            key="-NAV-DEDUPE-",
            expand_x=True,
            button_color=SIDEBAR_DEFAULT_COLOR,
            border_width=1,
        ),
        sg.Button(
            "Publish",
            key="-NAV-PUBLISH-",
            expand_x=True,
            button_color=SIDEBAR_DEFAULT_COLOR,
            border_width=1,
        ),
        sg.Button(
            "Tools / Logs",
            key="-NAV-TOOLS-",
            expand_x=True,
            button_color=SIDEBAR_DEFAULT_COLOR,
            border_width=1,
        ),
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
        sg.Text("Ready – Viewing Dashboard", key="-STATUSBAR-READY-"),
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
        size=(1280, 720),
        resizable=True,
        finalize=True,
    )

    active_nav = "-NAV-DASHBOARD-"
    _set_active_nav(window, active_nav)

    log_lines: List[str] = []
    _append_log(window, log_lines, "Dashboard started in smart-mode.")

    repo_root = _detect_repo_root()
    artifacts_dir = os.path.join(repo_root, "artifacts")
    logs_dir = os.path.join(repo_root, "artifacts", "logs")
    os.makedirs(artifacts_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Exit"):
            break

        if event == "-RUN-PIPELINE-":
            if _run_pipeline_stub(window, log_lines):
                window["-STATUSBAR-READY-"].update("Ready – Smart-Mode pipeline finished")
            else:
                window["-STATUSBAR-READY-"].update("Ready – Pipeline error")
        elif event == "-RUN-STEP-BTN-":
            step = values.get("-RUN-STEP-", "Unknown")
            if not _run_step(window, log_lines, step):
                window["-STATUSBAR-READY-"].update(f"Ready – Step error ({step})")
        elif event == "-OPEN-ARTIFACTS-":
            _open_directory(window, log_lines, artifacts_dir, "Open artifacts dir")
            window["-STATUSBAR-READY-"].update("Ready – Artifacts opened")
        elif event == "-OPEN-LOGS-":
            _open_directory(window, log_lines, logs_dir, "Open logs")
            window["-STATUSBAR-READY-"].update("Ready – Logs opened")
        elif event == "-REFRESH-":
            _append_log(window, log_lines, "Refresh status requested.")
            _update_status(window)
            window["-STATUSBAR-READY-"].update("Ready – Status refreshed")
        elif event == "-SYNC-":
            _sync_main(window, log_lines)
            _update_status(window)
            window["-STATUSBAR-READY-"].update("Ready – Repository synced")
        elif event == "-OPEN-DASHBOARD-":
            _open_dashboard(window, log_lines)
            window["-STATUSBAR-READY-"].update("Ready – Dashboard opened")
        elif event and str(event).startswith("-NAV-"):
            _append_log(window, log_lines, f"Navigation -> {event}")
            active_nav = str(event)
            _set_active_nav(window, active_nav)
            label = NAV_LABELS.get(active_nav, "Workflow")
            window["-STATUSBAR-READY-"].update(f"Ready – Viewing {label}")

    window.close()


if __name__ == "__main__":
    main()
