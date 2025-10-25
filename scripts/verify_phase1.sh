#!/usr/bin/env bash
set -euo pipefail
required=(
  "README.md"
  "docs/en/codex/architecture/sot.md"
  "docs/en/codex/architecture/taxonomy.md"
  "docs/en/codex/architecture/data-model.md"
  "docs/en/codex/phases/phase1_bootstrap.md"
  "docs/en/codex/runners/100.md"
  "docs/en/codex/progress.json"
  ".github/workflows/ci.yml"
  "scripts/python/extract_off_data.py"
  "scripts/python/normalize_products.py"
  "scripts/python/classify_products.py"
  "scripts/python/validate_gtin.py"
  "requirements.txt"
)
ok=1
for f in "${required[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "MISSING: $f"
    ok=0
  fi
done
if [[ $ok -eq 1 ]]; then
  echo "Phase 1 verification OK."
else
  echo "Phase 1 verification FAILED."
  exit 1
fi
