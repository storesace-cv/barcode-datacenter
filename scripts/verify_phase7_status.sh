#!/usr/bin/env bash
set -euo pipefail

echo "== Verify Phase 7 =="
test -f docs/en/codex/architecture/app-status-index.json
test -f docs/en/codex/architecture/app-status2gpt.md
test -f docs/en/codex/architecture/policies.md
test -f docs/en/codex/progress.json
test -f docs/en/codex/runners/700.md
test -f scripts/codex/progress_helper.py
test -f scripts/codex/run_smart_pipeline.py
test -f scripts/launchers/launch_gui.sh

# Dry-run pipeline stub (local check)
python3 scripts/codex/run_smart_pipeline.py

# Check artifact
test -f artifacts/logs/phase7_pipeline.log
echo "OK: Phase 7 verification passed."
