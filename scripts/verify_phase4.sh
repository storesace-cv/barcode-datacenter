#!/usr/bin/env bash
set -euo pipefail

PY="python3"
command -v "$PY" >/dev/null 2>&1 || { echo "python3 not found"; exit 1; }

# Ensure prerequisites
req=(
  "scripts/python/build_unify_input.py"
  "scripts/python/dedupe_unify.py"
  "scripts/python/validate_gtin.py"
  "scripts/python/normalize_products.py"
  "scripts/python/extract_off_data.py"
  "scripts/python/classify_products_v2.py"
)
for f in "${req[@]}"; do [[ -f "$f" ]] || { echo "MISSING: $f"; exit 1; }; done

# Prepare stub pipeline
$PY scripts/python/extract_off_data.py --country PT --limit 40 --out data/off_pt.jsonl
$PY scripts/python/normalize_products.py --in data/off_pt.jsonl --out data/normalized_pt.csv --country PT
$PY scripts/python/classify_products_v2.py --in data/normalized_pt.csv --out data/classified_pt_v2.csv --country PT
$PY scripts/python/validate_gtin.py --in data/classified_pt_v2.csv --out data/validated_pt.csv

# Build manifest and unify
$PY scripts/python/build_unify_input.py --out data/_unify_manifest.json
$PY scripts/python/dedupe_unify.py --manifest data/_unify_manifest.json --out-csv data/unified_all.csv --dup-report data/duplicates_report.csv

test -s data/unified_all.csv || { echo "Missing unified_all.csv"; exit 1; }
test -s data/duplicates_report.csv || { echo "Missing duplicates_report.csv"; exit 1; }

rows=$(wc -l < data/unified_all.csv | tr -d ' ')
if [ "$rows" -lt 2 ]; then echo "Too few unified rows"; exit 1; fi

echo "Phase 4 verification OK."
