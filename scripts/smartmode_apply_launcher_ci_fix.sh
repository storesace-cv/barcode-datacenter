#!/usr/bin/env bash
set -euo pipefail
BRANCH="${1:-my-barcode-datacenter}"
git checkout -B "$BRANCH"
git add -A
git commit -m "ci: launcher verification — self-sufficient verify + venv bootstrap [smart-mode]" || echo "Nothing to commit"
git push -u origin "$BRANCH"
echo "Launcher CI fix applied to $BRANCH."
