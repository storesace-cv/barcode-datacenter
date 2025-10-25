#!/usr/bin/env bash
set -euo pipefail

PY="python3"
command -v "$PY" >/dev/null 2>&1 || { echo "python3 not found. On macOS: brew install python@3.11"; exit 1; }

req=(
  "scripts/python/classify_products_v2.py"
  "data/seed/dictionaries/family_rules.csv"
  "data/seed/dictionaries/subfamily_rules.csv"
  "data/seed/dictionaries/brands_normalization.csv"
  "data/seed/dictionaries/synonyms_uom.csv"
  "docs/en/codex/runners/315.md"
  "docs/en/codex/runners/320.md"
  "docs/en/codex/phases/phase3_classify.md"
)
for f in "${req[@]}"; do
  [[ -f "$f" ]] || { echo "MISSING: $f"; exit 1; }
done

$PY scripts/python/extract_off_data.py --country PT --limit 20 --out data/off_pt_stub.jsonl
$PY scripts/python/normalize_products.py --in data/off_pt_stub.jsonl --out data/normalized_pt.csv --country PT
$PY scripts/python/classify_products_v2.py --in data/normalized_pt.csv --out data/classified_pt_v2.csv --country PT

test -s data/classified_pt_v2.csv || { echo "Empty output"; exit 1; }
rows=$(wc -l < data/classified_pt_v2.csv | tr -d ' ')
if [ "$rows" -lt 2 ]; then
  echo "Too few rows"; exit 1;
fi

echo "Phase 3 verification OK."
