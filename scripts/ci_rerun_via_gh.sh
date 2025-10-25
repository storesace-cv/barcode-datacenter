#!/usr/bin/env bash
set -euo pipefail
# Requires GitHub CLI authenticated: gh auth login
# Rerun the latest CI workflow on current branch
branch="$(git rev-parse --abbrev-ref HEAD)"
run_id="$(gh run list --workflow CI --branch "$branch" --limit 1 --json databaseId --jq '.[0].databaseId')"
if [[ -z "$run_id" ]]; then
  echo "No CI run found for branch $branch"; exit 1;
fi
gh run rerun "$run_id"
echo "Requested rerun for run_id=$run_id"
