#!/usr/bin/env bash
set -euo pipefail
BRANCH="${1:-my-barcode-datacenter}"

# Append SoT launcher venv section if SoT exists
SOT="docs/en/codex/architecture/sot.md"
APP="docs/en/codex/architecture/sot_launcher_venv.append.md"
if [ -f "$SOT" ] && [ -f "$APP" ]; then
  printf "\n\n" >> "$SOT"
  cat "$APP" >> "$SOT"
  rm -f "$APP"
fi

# Merge progress patch if jq is available
if command -v jq >/dev/null 2>&1 && [ -f docs/en/codex/progress.json ] && [ -f docs/en/codex/progress.json.patch ]; then
  tmp="$(mktemp)"
  jq -s '.[0] * .[1]' docs/en/codex/progress.json docs/en/codex/progress.json.patch > "$tmp"
  mv "$tmp" docs/en/codex/progress.json
  rm -f docs/en/codex/progress.json.patch
fi

# Append changelog if exists
if [ -f CHANGELOG.md ] && [ -f CHANGELOG.append.md ]; then
  printf "\n\n" >> CHANGELOG.md
  cat CHANGELOG.append.md >> CHANGELOG.md
  rm -f CHANGELOG.append.md
fi

git checkout -B "$BRANCH"
git add -A
git commit -m "phase6.1: codex+ci sync for venv-enforced launcher (runner 620) [smart-mode]" || echo "Nothing to commit"
git push -u origin "$BRANCH"
echo "Phase 6.1 sync applied to $BRANCH."
