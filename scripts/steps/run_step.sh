#!/usr/bin/env bash
set -euo pipefail

STEP="${1:-}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-python3}"

case "$STEP" in
  ingest)
    echo "[Smart-Mode] Running ingest step"
    exec "$PYTHON_BIN" -m pipeline.ingest
    ;;
  normalize)
    echo "[Smart-Mode] Running normalize step"
    exec "$PYTHON_BIN" -m pipeline.normalize
    ;;
  classify)
    echo "[Smart-Mode] Running classify step"
    exec "$PYTHON_BIN" -m pipeline.classify
    ;;
  validate_gtin|validate)
    echo "[Smart-Mode] Running validate GTIN step"
    exec "$PYTHON_BIN" -m pipeline.validate
    ;;
  dedupe_unify|dedupe)
    echo "[Smart-Mode] Running dedupe & unify step"
    exec "$PYTHON_BIN" -m pipeline.dedupe
    ;;
  publish)
    echo "[Smart-Mode] Running publish step"
    exec "$PYTHON_BIN" -m pipeline.publish
    ;;
  pipeline|run|all)
    echo "[Smart-Mode] Running full pipeline"
    exec "$PYTHON_BIN" -m pipeline.run
    ;;
  *)
    echo "[Smart-Mode] Unknown step: $STEP" >&2
    exit 1
    ;;
esac
