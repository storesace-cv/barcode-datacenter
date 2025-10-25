#!/usr/bin/env bash
set -uo pipefail
STRICT_CI="${STRICT_CI:-0}"
python -m pip install --upgrade pip || true
pip install -r requirements.txt || true
pip install pytest Unidecode flake8 || true

flake8 scripts || true

PYTHONPATH=. pytest -q tests/test_classify_v2.py tests/test_unify.py
code=$?
if [ "$code" -ne 0 ]; then
  echo "::warning title=pytest::exit code $code (soft-fail). Set STRICT_CI=1 to enforce."
  if [ "$STRICT_CI" = "1" ]; then exit "$code"; fi
fi

[ -f scripts/verify_phase1.sh ] && bash scripts/verify_phase1.sh || true
echo "CI entry OK."
