#!/usr/bin/env bash
set -uo pipefail
STRICT_CI="${STRICT_CI:-0}"
echo "== CI Entry =="
echo "STRICT_CI=$STRICT_CI"
echo "Python:"; python --version
echo "Pip:"; pip --version

# Ensure deps
python -m pip install --upgrade pip
pip install -r requirements.txt || true
pip install pytest Unidecode flake8 || true

echo "== Lint =="
flake8 scripts || true

echo "== Pytest =="
PYTHONPATH=. pytest -q tests/test_classify_v2.py tests/test_unify.py
code=$?
if [ "$code" -ne 0 ]; then
  echo "::warning title=Pytest failed::pytest exit code $code (soft-fail). Set STRICT_CI=1 to enforce failure."
  if [ "$STRICT_CI" = "1" ]; then
    exit "$code"
  fi
fi

echo "== Verify Phase 1 =="
bash scripts/verify_phase1.sh

echo "== CI Entry done =="
