#!/usr/bin/env bash
# Force reinstall of PySimpleGUI 4.60.5, with vendor fallback.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
source .venv/bin/activate 2>/dev/null || python3 -m venv .venv && source .venv/bin/activate

pip uninstall -y PySimpleGUI >/dev/null 2>&1 || true
pip cache purge >/dev/null 2>&1 || true
if ! pip install --no-cache-dir 'PySimpleGUI==4.60.5'; then
  echo "[fix] Public index unavailable. Trying vendor wheel..."
  WHEEL='vendor/PySimpleGUI-4.60.5-py3-none-any.whl'
  test -f "$WHEEL" || { echo "[fix] Missing $WHEEL"; exit 2; }
  pip install --no-cache-dir "$WHEEL"
fi

python - <<'PYCODE'
import PySimpleGUI as sg, sys
print("PySimpleGUI:", sg.version)
assert str(sg.version).startswith('4'), "Expected 4.x"
assert hasattr(sg, "theme")
print("Verification OK — v4.x detected.")
PYCODE
