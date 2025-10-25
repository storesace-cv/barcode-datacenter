#!/usr/bin/env bash
# Smart-Mode Launcher v3.3 — Prefer PySimpleGUI 4.x (fallback to vendor wheel)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
VENV_DIR="${ROOT}/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "[Smart-Mode] Launcher — initializing environment (prefer PySimpleGUI 4.x)"
echo "[Smart-Mode] Project root: ${ROOT}"

# 1) Create/activate venv
if [ ! -d "${VENV_DIR}" ]; then
  echo "[Smart-Mode] Creating virtual environment..."
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi
source "${VENV_DIR}/bin/activate"

# 2) Upgrade toolchain
python -m ensurepip -U >/dev/null 2>&1 || true
pip install --upgrade pip wheel setuptools >/dev/null 2>&1

ensure_psg4 () {
  echo "[Smart-Mode] Ensuring PySimpleGUI 4.x is installed..."
  # Try to import and verify version
  if python - <<'PYCODE'
import sys
try:
    import PySimpleGUI as sg
    ver = getattr(sg, 'version', 'unknown')
    if ver != 'unknown' and str(ver).startswith('4'):
        print('[Smart-Mode] Detected PySimpleGUI', ver, '(OK)')
        raise SystemExit(0)
except Exception:
    pass
raise SystemExit(1)
PYCODE
  then
    return 0
  fi

  echo "[Smart-Mode] Installing PySimpleGUI==4.60.5 from public index (best-known stable)"
  if pip install --no-cache-dir 'PySimpleGUI==4.60.5' >/dev/null 2>&1; then
    echo "[Smart-Mode] Installed PySimpleGUI 4.60.5"
  else
    echo "[Smart-Mode] Public index failed or version unavailable. Trying vendor wheel..."
    WHEEL='vendor/PySimpleGUI-4.60.5-py3-none-any.whl'
    if [ -f "$WHEEL" ]; then
      pip install --no-cache-dir "$WHEEL"
      echo "[Smart-Mode] Installed from vendor wheel: $WHEEL"
    else
      echo "[Smart-Mode] ❌ No vendor wheel found at $WHEEL"
      echo "[Smart-Mode] Please download PySimpleGUI 4.60.5 wheel and place it at: $WHEEL"
      echo "[Smart-Mode] Aborting."
      exit 2
    fi
  fi

  # Verify post-install API
  python - <<'PYCODE'
import PySimpleGUI as sg, sys
ver = getattr(sg, 'version', 'unknown')
print('[Smart-Mode] PySimpleGUI version now:', ver)
assert hasattr(sg, 'theme'), "Missing 'theme' attribute — installation broken"
if not str(ver).startswith('4'):
    sys.exit("Installed version is not 4.x; please provide vendor wheel 4.60.5")
print('[Smart-Mode] PySimpleGUI 4.x verified — OK')
PYCODE
}

ensure_psg4

# 3) Launch GUI (PySimpleGUI-based)
echo "[Smart-Mode] Launching GUI..."
python app/gui/gui_app.py || {
  echo "[Smart-Mode] ❌ GUI crashed, collecting logs"
  mkdir -p logs
  date -u +"[%FT%TZ] GUI launch failed" >> logs/launcher_error.log
  exit 1
}

# 4) Update Codex + push to GitHub
if [ -f "scripts/codex/update_codex_and_push.sh" ]; then
  echo "[Smart-Mode] Updating Codex + pushing state to GitHub..."
  bash scripts/codex/update_codex_and_push.sh "launcher_pysimplegui4_ok"
fi

echo "[Smart-Mode] ✅ Environment ready and GUI launched (PySimpleGUI 4.x)"
