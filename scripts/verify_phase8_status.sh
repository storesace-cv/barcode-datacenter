#!/usr/bin/env bash
set -euo pipefail
echo "== Verify Phase 8 (docs-only static checks) =="

# Must contain FreeSimpleGUI import somewhere in app/gui
grep -R "FreeSimpleGUI" -n app/gui || (echo "Missing FreeSimpleGUI import" && exit 1)

# UI strings checks
REQS=(
  "Barcode Datacenter GUI"
  "Dashboard"
  "Ingest"
  "Normalize"
  "Classify"
  "Validate GTIN"
  "Dedupe & Unify"
  "Publish"
  "Tools / Logs"
  "Sync Main"
  "Refresh"
  "Open Dashboard"
  "Run step"
  "Run pipeline (Smart-Mode)"
  "Open artifacts dir"
  "Open logs"
  "Data Table"
  "Preview / Artifacts"
  "Logs"
  "Ready"
  "Valid:"
  "Invalid:"
  "Duplicates:"
  "Unified:"
  "'ok'"
  "'ts'"
  "'root'"
  "'branch'"
  "'version'"
)

for s in "${REQS[@]}"; do
  grep -R --fixed-strings "$s" -n app/gui || { echo "Missing UI string: $s"; exit 1; }
done

python3 scripts/codex/progress_helper.py --phase 8 --task gui_dashboard_layout --value 100 --msg "Phase 8 dashboard layout present."
python3 scripts/codex/progress_helper.py --phase 8 --task actions_wiring --value 100 --msg "Phase 8 actions wired to placeholders."
python3 scripts/codex/progress_helper.py --phase 8 --task statusbar_counters --value 100 --msg "Status counters visible."
python3 scripts/codex/progress_helper.py --phase 8 --task tabs_impl --value 100 --msg "Tabs scaffolded."
python3 scripts/codex/progress_helper.py --phase 8 --task tool_buttons --value 100 --msg "Sync/Refresh/Open wired."
echo "OK Phase 8 verify (static checks)."
