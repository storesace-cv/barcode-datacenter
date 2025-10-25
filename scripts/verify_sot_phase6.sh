#!/usr/bin/env bash
set -euo pipefail
test -f "docs/en/codex/architecture/sot.md" || { echo "Missing SoT"; exit 1; }
grep -q "Phase 6 — Desktop GUI (pywebview)" docs/en/codex/architecture/sot.md || { echo "Phase 6 section not found"; exit 1; }
echo "SoT Phase 6 OK."
