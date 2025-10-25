#!/usr/bin/env bash
# Verify pinned PySimpleGUI-4-foss version and API

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source .venv/bin/activate 2>/dev/null || true

python - <<'PYCODE'
import PySimpleGUI as sg, sys
ver = str(getattr(sg, 'version', 'unknown'))
print("Detected PySimpleGUI-4-foss:", ver)
if not ver.startswith("4.61.0.206"):
    sys.exit(f"❌ Expected 4.61.0.206, got {ver}")
assert hasattr(sg, "theme"), "Missing sg.theme"
print("✅ OK — PySimpleGUI-4-foss pinned and usable")
PYCODE
