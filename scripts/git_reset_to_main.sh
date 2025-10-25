#!/usr/bin/env bash
set -euo pipefail
BR="${1:-my-barcode-datacenter}"
mkdir -p .local_backup && tar -czf ".local_backup/data_$(date +%Y%m%d_%H%M%S).tgz" data artifacts 2>/dev/null || true
git fetch --all
git checkout "$BR"
git reset --hard origin/main
git push -f origin "$BR"
echo "Branch $BR now matches origin/main."
