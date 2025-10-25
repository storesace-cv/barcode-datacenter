#!/usr/bin/env bash
set -euo pipefail
BRANCH="${1:-my-barcode-datacenter}"
if [ -f README.md ] && [ -f README_APPEND_ROADMAP.md ]; then
  printf "\n\n" >> README.md
  cat README_APPEND_ROADMAP.md >> README.md
  rm -f README_APPEND_ROADMAP.md
fi
git checkout -B "$BRANCH"
git add -A
git commit -m "docs: README v2 (Smart-Mode) — SoT/Taxonomy/DataModel/GUI integrated [smart-mode]" || echo "Nothing to commit"
git push -u origin "$BRANCH"
echo "README v2 applied to $BRANCH."
