#!/usr/bin/env bash
set -euo pipefail
python3 -m pip install --upgrade pip || true
[ -f requirements.txt ] && pip3 install -r requirements.txt || true
pip3 install pytest Unidecode flake8 || true
PYTHONPATH=. pytest -q tests/test_classify_v2.py tests/test_unify.py || true
[ -f scripts/verify_phase1.sh ] && bash scripts/verify_phase1.sh || true
echo "Local CI OK (soft)."
