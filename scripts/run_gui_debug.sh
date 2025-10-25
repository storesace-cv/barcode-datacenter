#!/usr/bin/env bash
set -euo pipefail
export PYTHONUNBUFFERED=1
exec python3 scripts/python/gui_backend.py 2>&1 | tee .smartmode/gui_debug_$(date +%Y%m%d_%H%M%S).log
