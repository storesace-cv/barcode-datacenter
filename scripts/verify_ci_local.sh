#!/usr/bin/env bash
set -euo pipefail
echo "== Env =="
python3 --version || true
pip --version || true
echo "== Install =="
python3 -m pip install --upgrade pip
[ -f requirements.txt ] && pip install -r requirements.txt || true
echo "== Pytest =="
PYTHONPATH=. pytest -q || { echo 'pytest failed locally'; exit 1; }
echo "== Verify P1 =="
bash scripts/verify_phase1.sh
echo "== DONE : local CI OK =="
