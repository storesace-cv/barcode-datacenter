#!/usr/bin/env bash
set -euo pipefail
BRANCH="${1:-my-barcode-datacenter}"
git checkout -B "$BRANCH"
SOT="docs/en/codex/architecture/sot.md"
APPEND="docs/en/codex/architecture/sot_launcher.append.md"
if [ -f "$SOT" ] && [ -f "$APPEND" ]; then
  printf "\n\n" >> "$SOT"
  cat "$APPEND" >> "$SOT"
  rm -f "$APPEND"
fi
if command -v jq >/dev/null 2>&1 && [ -f docs/en/codex/progress.json ] && [ -f docs/en/codex/progress.json.patch ]; then
  tmp="$(mktemp)"
  jq -s '.[0] * .[1]' docs/en/codex/progress.json docs/en/codex/progress.json.patch > "$tmp"
  mv "$tmp" docs/en/codex/progress.json
  rm -f docs/en/codex/progress.json.patch
fi
git add -A
git commit -m "phase7: launcher integration (runner 700, verify + CI, SoT update) [smart-mode]" || echo "Nothing to commit"
git push -u origin "$BRANCH"
echo "Smart-Mode Phase 7 update pushed to $BRANCH."
