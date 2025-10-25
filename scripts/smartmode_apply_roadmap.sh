#!/usr/bin/env bash
set -euo pipefail
BRANCH="${1:-my-barcode-datacenter}"
git checkout -B "$BRANCH"
if command -v jq >/dev/null 2>&1 && [ -f docs/en/codex/progress.json ] && [ -f docs/en/codex/progress.json.patch ]; then
  tmp="$(mktemp)"; jq -s '.[0] * .[1]' docs/en/codex/progress.json docs/en/codex/progress.json.patch > "$tmp"
  mv "$tmp" docs/en/codex/progress.json; rm -f docs/en/codex/progress.json.patch
fi
git add -A
git commit -m "docs: roadmap + progress sync [smart-mode]" || echo "Nothing to commit"
git push -u origin "$BRANCH"
echo "Roadmap applied to $BRANCH."
