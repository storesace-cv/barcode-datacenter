#!/usr/bin/env bash
set -euo pipefail
req=(
  "scripts/python/gui_backend.py"
  "gui/index.html"
  "gui/app.js"
  "gui/style.css"
  "gui/dashboard.html"
)
ok=1
for f in "${req[@]}"; do
  [[ -f "$f" ]] || { echo "MISSING: $f"; ok=0; }
done
python3 -m py_compile scripts/python/gui_backend.py
if [[ $ok -eq 1 ]]; then
  echo "Phase 6 (GUI) verification OK."
else
  echo "Phase 6 (GUI) verification FAILED."
  exit 1
fi
