#!/usr/bin/env bash
set -euo pipefail
# Usage: bash scripts/smartmode_optionB_apply_and_push.sh /path/to/repo my-branch
REPO="${1:-$(pwd)}"
BRANCH="${2:-my-barcode-datacenter}"

echo ">> [OptionB] Apply bundle to working tree and push branch"
BUNDLE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$REPO"
git fetch origin
git checkout "$BRANCH" || git checkout -b "$BRANCH" origin/"$BRANCH" || git checkout -b "$BRANCH"

# Ensure dirs
mkdir -p "$REPO/docs/en/codex/architecture"          "$REPO/docs/en/codex/runners"          "$REPO/scripts/codex"          "$REPO/scripts/launchers"          "$REPO/.github/workflows"          "$REPO/app/gui"          "$REPO/artifacts/logs"

# Copy content
cp -R "$BUNDLE_ROOT/docs/."     "$REPO/docs/"
cp -R "$BUNDLE_ROOT/scripts/."  "$REPO/scripts/"
cp -R "$BUNDLE_ROOT/.github/."  "$REPO/.github/"
cp -R "$BUNDLE_ROOT/app/."      "$REPO/app/"

# Exec bits
chmod +x "$REPO/scripts/launchers/launch_gui.sh" || true
chmod +x "$REPO/scripts/verify_phase7_status.sh" || true
chmod +x "$REPO/scripts/codex/run_smart_pipeline.py" || true
chmod +x "$REPO/scripts/codex/progress_helper.py" || true
chmod +x "$REPO/scripts/smartmode_optionB_apply_and_push.sh" || true
chmod +x "$REPO/scripts/codex/wait_codex_and_pull.sh" || true

git add docs scripts .github app || true
git commit -m "phase7: add SoT + runner 700 + CI + OptionB policy" || true
git push origin "$BRANCH"
echo ">> [OptionB] Branch pushed. Next: merge FF to main and let Codex run."
