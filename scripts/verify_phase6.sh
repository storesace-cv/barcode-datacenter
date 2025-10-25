#!/usr/bin/env bash
set -euo pipefail
# Self-test does not require pywebview; only checks that index.html exists and server responds.
python3 scripts/python/gui_backend.py --selftest
echo "Phase 6 verification OK."
