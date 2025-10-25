#!/usr/bin/env bash
# Force reinstall of PySimpleGUI 4.x in the current repo venv (idempotent).

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
VENV_DIR="${ROOT}/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ ! -d "${VENV_DIR}" ]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi
source "${VENV_DIR}/bin/activate"

pip uninstall -y PySimpleGUI >/dev/null 2>&1 || true
pip cache purge >/dev/null 2>&1 || true
pip install 'PySimpleGUI<5.0.0'

python - <<'PYCODE'
import PySimpleGUI as sg
print("PySimpleGUI version:", sg.version)
assert hasattr(sg, "theme")
print("Verification OK — v4.x detected.")
PYCODE
