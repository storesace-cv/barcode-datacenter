#!/usr/bin/env bash
# Verify pinned FreeSimpleGUI version and API

set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source .venv/bin/activate 2>/dev/null || true

python - <<'PYCODE'
import FreeSimpleGUI as sg, sys
ver = str(getattr(sg, 'version', 'unknown'))
print("Detected FreeSimpleGUI:", ver)
EXPECTED_MAJOR = "5.2"
if not ver.startswith(EXPECTED_MAJOR):
    sys.exit(f"❌ Expected {EXPECTED_MAJOR}.x, got {ver}")
assert hasattr(sg, "theme"), "Missing sg.theme"
print("✅ OK — FreeSimpleGUI pinned and usable")
PYCODE
