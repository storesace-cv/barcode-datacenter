#!/usr/bin/env bash
set -euo pipefail

BRANCH="${1:-my-barcode-datacenter}"
REPO_ROOT="$(pwd)"

# Ensure on branch
git checkout -B "$BRANCH"

# Apply progress patch if jq available; else just add files
if command -v jq >/dev/null 2>&1 && [ -f docs/en/codex/progress.json ] && [ -f docs/en/codex/progress.json.patch ]; then
  tmp="$(mktemp)"
  jq -s '.[0] * .[1]' docs/en/codex/progress.json docs/en/codex/progress.json.patch > "$tmp"
  mv "$tmp" docs/en/codex/progress.json
  rm -f docs/en/codex/progress.json.patch
fi

git add docs/en/codex/architecture/sot.md         docs/en/codex/runners/605.md         docs/en/codex/phases/phase6_checklist.md         docs/en/codex/progress.json         docs/en/codex/progress.json.patch || true

# If patch removed, it's fine
git commit -m "phase6: SoT updated, runner 605, checklist, progress [smart-mode]" || echo "Nothing to commit"

git push -u origin "$BRANCH"
echo "Smart-Mode Phase 6 update pushed to $BRANCH."
