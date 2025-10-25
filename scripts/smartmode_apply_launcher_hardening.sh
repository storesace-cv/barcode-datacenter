#!/usr/bin/env bash
set -euo pipefail
BRANCH="${1:-my-barcode-datacenter}"
# Append .gitignore rules if not present
grep -q ".local_backup/" .gitignore 2>/dev/null || printf "\n.local_backup/\n.smartmode/\n" >> .gitignore
git rm -r --cached .local_backup 2>/dev/null || true
git checkout -B "$BRANCH"
git add -A
git commit -m "launcher: hardening — backups outside repo + git guards [smart-mode]" || echo "Nothing to commit"
git push -u origin "$BRANCH"
echo "Launcher hardening applied to $BRANCH."
