#!/usr/bin/env bash
# Force reinstall of pinned PySimpleGUI-4-foss version (idempotent)

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Ensure venv
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

pip uninstall -y PySimpleGUI PySimpleGUI-4-foss >/dev/null 2>&1 || true
pip install --no-cache-dir "PySimpleGUI-4-foss==4.61.0.206"

python - <<'PYCODE'
import PySimpleGUI as sg, sys
ver = str(getattr(sg, 'version', 'unknown'))
print("PySimpleGUI-4-foss version:", ver)
assert ver.startswith("4.61.0.206"), f"Expected 4.61.0.206, got {ver}"
assert hasattr(sg, "theme")
print("Verification OK — pinned version installed.")
PYCODE
