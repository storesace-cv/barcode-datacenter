#!/usr/bin/env bash
set -euo pipefail
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt || true
pip3 install pytest Unidecode flake8
PYTHONPATH=. pytest -q tests/test_classify_v2.py tests/test_unify.py
bash scripts/verify_phase1.sh
echo "CI quick test OK"
