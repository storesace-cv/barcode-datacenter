#!/usr/bin/env bash
set -euo pipefail
BRANCH="${1:-my-barcode-datacenter}"
git checkout -B "$BRANCH"
git add -A
git commit -m "gui: serve gui/index.html at :6754 + selftest + workflow [smart-mode]" || echo "Nothing to commit"
git push -u origin "$BRANCH"
echo "GUI fix applied to $BRANCH."
