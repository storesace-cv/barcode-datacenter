#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
for step in ingest normalize classify validate_gtin dedupe_unify publish; do
  bash scripts/steps/run_step.sh "$step"
done
