#!/usr/bin/env bash
# Force reinstall of pinned FreeSimpleGUI version (idempotent)

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

# Ensure venv
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate

pip uninstall -y PySimpleGUI PySimpleGUI-4-foss FreeSimpleGUI >/dev/null 2>&1 || true
pip install --no-cache-dir "FreeSimpleGUI==5.2.0.post1"

python - <<'PYCODE'
import FreeSimpleGUI as sg, sys
ver = str(getattr(sg, 'version', 'unknown'))
print("FreeSimpleGUI version:", ver)
assert ver.startswith("5.2.0"), f"Expected 5.2.0*, got {ver}"
assert hasattr(sg, "theme")
print("Verification OK — pinned version installed.")
PYCODE
