#!/usr/bin/env bash
# Smart-Mode Launcher v3.2 — Barcode Datacenter
# Reverts GUI dependency to PySimpleGUI 4.x (non-pro) for CI/Codex compatibility.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
VENV_DIR="${ROOT}/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "[Smart-Mode] Launcher — initializing environment"
echo "[Smart-Mode] Project root: ${ROOT}"

# (1) Create / refresh venv
if [ ! -d "${VENV_DIR}" ]; then
  echo "[Smart-Mode] Creating virtual environment..."
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi
source "${VENV_DIR}/bin/activate"

# (2) Guarantee pip toolchain
python -m ensurepip -U >/dev/null 2>&1 || true
pip install --upgrade pip wheel setuptools >/dev/null 2>&1

# (3) Install PySimpleGUI 4.x (non-pro) from public PyPI (idempotent)
echo "[Smart-Mode] Installing PySimpleGUI 4.x (stable, non-pro)..."
pip uninstall -y PySimpleGUI >/dev/null 2>&1 || true
pip cache purge >/dev/null 2>&1 || true
pip install 'PySimpleGUI<5.0.0' >/dev/null 2>&1

# (4) Verify installation
python - <<'PYCODE'
import PySimpleGUI as sg, sys
assert hasattr(sg, "theme"), "PySimpleGUI missing 'theme' attribute"
print("[Smart-Mode] PySimpleGUI 4.x verified — OK")
PYCODE

# (5) Launch GUI
echo "[Smart-Mode] Launching GUI..."
python app/gui/gui_app.py || {
  echo "[Smart-Mode] ❌ GUI crashed, collecting logs"
  mkdir -p logs
  date -u +"[%FT%TZ] GUI launch failed" >> logs/launcher_error.log
  exit 1
}

# (6) Update Codex + push to GitHub
echo "[Smart-Mode] Updating Codex + pushing state to GitHub..."
bash scripts/codex/update_codex_and_push.sh "launcher_fix_pysimplegui4"

echo "[Smart-Mode] ✅ Environment ready and GUI launched (PySimpleGUI 4.x)"
