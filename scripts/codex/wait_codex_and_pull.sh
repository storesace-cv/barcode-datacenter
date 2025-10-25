#!/usr/bin/env bash
set -euo pipefail
# Polls for Codex completion by checking progress.json on main, then pulls.
# Usage: bash scripts/codex/wait_codex_and_pull.sh /path/to/repo 7 gui_wiring 100 600
REPO="${1:-$(pwd)}"
PHASE="${2:-7}"
TASK="${3:-gui_wiring}"
TARGET_VALUE="${4:-100}"
TIMEOUT="${5:-600}"  # seconds

cd "$REPO"
echo ">> Waiting for Codex to complete phase=$PHASE task=$TASK (target>=$TARGET_VALUE)"

START=$(date +%s)
while true; do
  git fetch origin
  git checkout main
  git pull --ff-only || true
  if [ -f "docs/en/codex/progress.json" ]; then
    VAL=$(python3 - <<'PY'
import json,sys
p="docs/en/codex/progress.json"
j=json.load(open(p,encoding="utf-8"))
print(j.get("phases",{}).get(sys.argv[1],{}).get("tasks",{}).get(sys.argv[2],{}).get("value",-1))
PY
    "$PHASE" "$TASK")
    if [ "$VAL" -ge "$TARGET_VALUE" ] 2>/dev/null; then
      echo ">> Codex complete (value=$VAL). Pulling main done."
      break
    fi
  fi
  NOW=$(date +%s)
  if [ $((NOW-START)) -ge "$TIMEOUT" ]; then
    echo "!! Timeout waiting for Codex."
    exit 1
  fi
  sleep 10
done
