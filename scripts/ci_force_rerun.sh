#!/usr/bin/env bash
set -euo pipefail
msg="${1:-ci: trigger manual rerun}"
git commit --allow-empty -m "$msg"
git push
echo "Pushed empty commit to trigger CI."
