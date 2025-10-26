#!/usr/bin/env bash
set -euo pipefail
echo "== Verify Phase 9 (docs-only checks) =="

REQS=(
  "pipeline/ingest.py"
  "pipeline/normalize.py"
  "pipeline/classify.py"
  "pipeline/validate.py"
  "pipeline/dedupe.py"
  "pipeline/publish.py"
)

missing=0
for f in "${REQS[@]}"; do
  if [ ! -f "$f" ]; then
    echo "Missing: $f"
    missing=1
  fi
done

if ls app/gui/*.py >/dev/null 2>&1; then
  grep -R "FreeSimpleGUI" -n app/gui || echo "WARN: FreeSimpleGUI import not found in GUI yet."
fi

if [ $missing -eq 0 ]; then
  echo "Phase 9 modules present (basic check)."
else
  echo "Modules missing (expected before Codex runs)."
fi
