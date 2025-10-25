#!/usr/bin/env bash
# Self-sufficient verify: creates .venv if missing and runs checks
set -euo pipefail

ROOT="$(pwd)"
VENV="$ROOT/.venv"
PY="$(command -v python3 || true)"

if [ ! -x "$VENV/bin/python" ]; then
  if [ -z "$PY" ]; then
    echo "python3 not found"; exit 127
  fi
  "$PY" -m venv "$VENV"
  "$VENV/bin/python" -m pip install -U pip >/dev/null
fi

CUR="$("$VENV/bin/python" -c 'import sys; print(sys.executable)')"
case "$CUR" in
  */.venv/bin/python) echo "VENV OK: $CUR";;
  *) echo "Unexpected python: $CUR"; exit 2;;
esac

# Import backend to ensure path is valid
"$VENV/bin/python" - <<'PY'
import importlib.util, sys, os
p = os.path.join("scripts","python","gui_backend.py")
assert os.path.isfile(p), f"Missing {p}"
spec = importlib.util.spec_from_file_location("gui_backend", p)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print("Backend import OK")
PY

echo "Launcher venv verification OK."
