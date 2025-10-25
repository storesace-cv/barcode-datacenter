#!/usr/bin/env bash
set -euo pipefail
# Creates an empty commit to trigger CI (push-based) when workflow_dispatch isn't used.
msg="${1:-ci: force rerun [smart-mode]}"
git add -A || true
git commit --allow-empty -m "$msg" || true
git push
echo "Pushed. CI should run on this branch."
