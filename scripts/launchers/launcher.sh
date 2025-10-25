#!/usr/bin/env bash
# Smart-Mode Launcher v3.4 — Pin PySimpleGUI-4-foss==4.61.0.206
# Idempotent, CI-friendly, Codex/GitHub integrated

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
VENV_DIR="${ROOT}/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "[Smart-Mode] Launcher — initializing environment"
echo "[Smart-Mode] Project root: ${ROOT}"

# (1) Create / activate venv
if [ ! -d "${VENV_DIR}" ]; then
  echo "[Smart-Mode] Creating virtual environment..."
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi
# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"

# (2) Upgrade toolchain
python -m ensurepip -U >/dev/null 2>&1 || true
pip install --upgrade pip wheel setuptools >/dev/null 2>&1

# (3) Install pinned GUI lib (FOSS)
echo "[Smart-Mode] Installing PySimpleGUI-4-foss==4.61.0.206..."
pip uninstall -y PySimpleGUI PySimpleGUI-4-foss >/dev/null 2>&1 || true
pip install --no-cache-dir "PySimpleGUI-4-foss==4.61.0.206" >/dev/null 2>&1

# (4) Verify installation (exact version + API contract)
python - <<'PYCODE'
import sys
import PySimpleGUI as sg
ver = str(getattr(sg, 'version', 'unknown'))
print("[Smart-Mode] Detected PySimpleGUI-4-foss:", ver)
assert ver.startswith("4.61.0.206"), f"Expected 4.61.0.206, got {ver}"
assert hasattr(sg, "theme"), "Missing sg.theme"
print("[Smart-Mode] ✅ PySimpleGUI-4-foss verified")
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
if [ -f "scripts/codex/update_codex_and_push.sh" ]; then
  echo "[Smart-Mode] Updating Codex + pushing state to GitHub..."
  bash scripts/codex/update_codex_and_push.sh "deps_pysimplegui4foss_4.61.0.206"
fi

echo "[Smart-Mode] ✅ Environment ready and GUI launched (PySimpleGUI-4-foss 4.61.0.206)"
