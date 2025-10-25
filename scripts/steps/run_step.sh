#!/usr/bin/env bash
set -euo pipefail
STEP="${1:-}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
echo "[Smart-Mode] Running step: $STEP"
