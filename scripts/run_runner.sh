#!/usr/bin/env bash
set -euo pipefail
id="${1:-}"
case "$id" in
  100) bash scripts/verify_phase1.sh ;;
  110) bash scripts/verify_env.sh ;;
  200) python scripts/python/extract_off_data.py --country PT --limit 200 --out data/off_sample_pt.jsonl ;;
  300) python scripts/python/normalize_products.py --in data/off_sample_pt.jsonl --out data/normalized_pt.csv --country PT ;;
  310) python scripts/python/classify_products.py --in data/normalized_pt.csv --out data/classified_pt.csv --country PT ;;
  400) python scripts/python/validate_gtin.py --in data/classified_pt.csv --out data/validated_pt.csv ;;
  *) echo "Unknown runner id"; exit 2 ;;
esac
