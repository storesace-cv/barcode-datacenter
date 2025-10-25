#!/usr/bin/env bash
set -euo pipefail
BRANCH="${1:-my-barcode-datacenter}"

git checkout -B "$BRANCH"

# Merge progress patch if jq present and patch file exists
if command -v jq >/dev/null 2>&1 && [ -f docs/en/codex/progress.json ] && [ -f docs/en/codex/progress.json.patch ]; then
  tmp="$(mktemp)"
  jq -s '.[0] * .[1]' docs/en/codex/progress.json docs/en/codex/progress.json.patch > "$tmp"
  mv "$tmp" docs/en/codex/progress.json
  rm -f docs/en/codex/progress.json.patch
fi

# Stage files that may or may not exist; ignore missing
git add -A

git commit -m "phase3: dictionaries + classify v2 + verify + CI [smart-mode]" || echo "Nothing to commit"
git push -u origin "$BRANCH"
echo "Smart-Mode Phase 3 update pushed to $BRANCH."
