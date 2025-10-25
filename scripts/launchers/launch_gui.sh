#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

PYTHON_BIN="${PYTHON_BIN:-python3}"
TARGET_SPEC="${TARGET_SPEC:-FreeSimpleGUI>=5.2.0}"

cd "$REPO_ROOT"

echo "[Smart-Mode] Checking FreeSimpleGUI availability..."
if ! "$PYTHON_BIN" - <<'PYCODE'
import sys

try:
    import FreeSimpleGUI  # type: ignore
except ModuleNotFoundError:
    sys.exit(1)
except Exception:
    # Unexpected import error, force reinstall
    sys.exit(2)
PYCODE
then
  echo "[Smart-Mode] Installing ${TARGET_SPEC} via pip..."
  "$PYTHON_BIN" -m pip install --upgrade "${TARGET_SPEC}"
  echo "[Smart-Mode] ✅ FreeSimpleGUI installed"
else
  echo "[Smart-Mode] ✅ FreeSimpleGUI already present"
fi

exec "$PYTHON_BIN" -m app.gui.gui_app
