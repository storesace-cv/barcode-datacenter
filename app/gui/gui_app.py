import subprocess
import sys
import PySimpleGUI as sg


def _apply_theme(theme_name: str) -> None:
    """Apply the desired theme while remaining compatible with legacy releases."""

    if hasattr(sg, "theme"):
        sg.theme(theme_name)
        return

    if hasattr(sg, "change_look_and_feel"):
        sg.change_look_and_feel(theme_name)
        return

    # Fallback: some degraded versions of PySimpleGUI omit theme helpers entirely.
    # In this situation the GUI still runs, just without a custom look-and-feel.
    print(
        "Warning: Unable to configure PySimpleGUI theme – continuing with defaults.",
        file=sys.stderr,
    )


_apply_theme("DarkGrey13")
layout = [
    [sg.Text("Barcode Datacenter GUI (Smart-Mode)")],
    [sg.Button("Run pipeline (Smart-Mode)"), sg.Button("Exit")]
]
window = sg.Window("Barcode Datacenter GUI (Smart-Mode)", layout)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, "Exit"):
        break
    if event == "Run pipeline (Smart-Mode)":
        # Invoke Smart-Mode pipeline stub (idempotent)
        try:
            subprocess.check_call([sys.executable, "scripts/codex/run_smart_pipeline.py"])
            sg.popup("Pipeline executed (stub Smart-Mode)")
        except Exception as e:
            sg.popup_error(f"Pipeline failed: {e}")

window.close()
