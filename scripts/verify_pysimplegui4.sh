#!/usr/bin/env bash
# Verify that PySimpleGUI is 4.x and exposes expected API

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
source "${ROOT}/.venv/bin/activate" 2>/dev/null || { echo "venv not active"; exit 1; }

python - <<'PYCODE'
import PySimpleGUI as sg, sys
ver = getattr(sg, 'version', 'unknown')
print("Detected PySimpleGUI:", ver)
if ver.startswith("5"):
    sys.exit("❌ Detected v5.x (Pro). Expected v4.x")
assert hasattr(sg, "theme")
print("✅ OK — API present and version < 5")
PYCODE
