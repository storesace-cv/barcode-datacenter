#!/usr/bin/env bash
set -euo pipefail
BR="${1:-my-barcode-datacenter}"
git fetch origin
git checkout "$BR"
git rebase origin/main || git merge --no-ff origin/main -m "sync: main -> $BR [smart-mode]"
echo "Branch $BR synced with origin/main."
