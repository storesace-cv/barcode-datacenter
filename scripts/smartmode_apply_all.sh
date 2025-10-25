#!/usr/bin/env bash
# Smart-Mode one-shot apply: README v2, roadmap, workflows, progress merge and push
set -euo pipefail
BRANCH="${1:-my-barcode-datacenter}"

# Append README roadmap if present
if [ -f README.md ] && [ -f README_APPEND_ROADMAP.md ]; then
  printf "\n\n" >> README.md
  cat README_APPEND_ROADMAP.md >> README.md
  rm -f README_APPEND_ROADMAP.md
fi

# Merge progress patch if jq and files exist
if command -v jq >/dev/null 2>&1 && [ -f docs/en/codex/progress.json ] && [ -f docs/en/codex/progress.json.patch ]; then
  tmp="$(mktemp)"
  jq -s '.[0] * .[1]' docs/en/codex/progress.json docs/en/codex/progress.json.patch > "$tmp"
  mv "$tmp" docs/en/codex/progress.json
  rm -f docs/en/codex/progress.json.patch
fi

git checkout -B "$BRANCH"
git add -A
git commit -m "smart-mode: apply README v2 + helpers + workflows [bundle]" || echo "Nothing to commit"
git push -u origin "$BRANCH"
echo "Smart-Mode bundle applied to $BRANCH."
