#!/usr/bin/env bash
set -euo pipefail
BRANCH="${1:-my-barcode-datacenter}"

git checkout -B "$BRANCH"

# Merge progress patch if possible (optional)
if command -v jq >/dev/null 2>&1 && [ -f docs/en/codex/progress.json ] && [ -f docs/en/codex/progress.json.patch ]; then
  tmp="$(mktemp)"
  jq -s '.[0] * .[1]' docs/en/codex/progress.json docs/en/codex/progress.json.patch > "$tmp"
  mv "$tmp" docs/en/codex/progress.json
  rm -f docs/en/codex/progress.json.patch
fi

# Stage everything (robust)
git add -A

git commit -m "phase4: unify (manifest, dedupe/unify, verify, CI) [smart-mode]" || echo "Nothing to commit"
git push -u origin "$BRANCH"
echo "Smart-Mode Phase 4 update pushed to $BRANCH."
