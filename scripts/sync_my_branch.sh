#!/usr/bin/env bash
set -euo pipefail
branch="my-barcode-datacenter"
git fetch origin || true
git switch -c "$branch" 2>/dev/null || git switch "$branch"
git pull --rebase origin main || true
git status
echo "Your branch '$branch' is aligned to main (rebased where possible)."
