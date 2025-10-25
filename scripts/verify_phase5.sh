#!/usr/bin/env bash
set -euo pipefail
PY="python3"
command -v "$PY" >/dev/null 2>&1 || { echo "python3 not found"; exit 1; }

# Ensure exporter exists
test -f scripts/python/export_artifacts.py || { echo "Missing exporter"; exit 1; }

# If no unified_all.csv, build minimal pipeline
if [ ! -s data/unified_all.csv ]; then
  $PY scripts/python/extract_off_data.py --country PT --limit 20 --out data/off_pt.jsonl
  $PY scripts/python/normalize_products.py --in data/off_pt.jsonl --out data/normalized_pt.csv --country PT
  $PY scripts/python/classify_products_v2.py --in data/normalized_pt.csv --out data/classified_pt_v2.csv --country PT
  $PY scripts/python/validate_gtin.py --in data/classified_pt_v2.csv --out data/validated_pt.csv
  $PY scripts/python/build_unify_input.py --out data/_unify_manifest.json
  $PY scripts/python/dedupe_unify.py --manifest data/_unify_manifest.json --out-csv data/unified_all.csv --dup-report data/duplicates_report.csv
fi

# Export artifacts
$PY scripts/python/export_artifacts.py --in data/unified_all.csv --outdir artifacts

# Check files
for f in artifacts/barcode_unified.csv artifacts/barcode_unified.jsonl artifacts/barcode_unified.sqlite; do
  [ -s "$f" ] || { echo "Missing artifact: $f"; exit 1; }
done

echo "Phase 5 verification OK."
