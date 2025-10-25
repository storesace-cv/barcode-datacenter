import subprocess
import sys
import PySimpleGUI as sg

sg.theme("DarkGrey13")
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
