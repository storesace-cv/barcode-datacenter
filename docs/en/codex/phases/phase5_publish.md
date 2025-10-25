# Phase 5 — Publish (CSV/SQLite/JSONL + Release)

**Status:** ready · **Updated:** 2025-10-25

**Goal:** Exportar artefactos finais (CSV/SQLite/JSONL) para a pasta `artifacts/` e automatizar *GitHub Release*.

## Inputs
- `data/unified_all.csv` (Phase 4)

## Outputs
- `artifacts/barcode_unified.csv` (cópia normalizada)
- `artifacts/barcode_unified.jsonl` (JSONL)
- `artifacts/barcode_unified.sqlite` (SQLite com tabela `products` + índices)

## Runners
- `500` — Publish (gera artefactos localmente)

## Comandos
```bash
# Se ainda não existir, gerar unified_all.csv (stub)
python3 scripts/python/extract_off_data.py --country PT --limit 40 --out data/off_pt.jsonl
python3 scripts/python/normalize_products.py --in data/off_pt.jsonl --out data/normalized_pt.csv --country PT
python3 scripts/python/classify_products_v2.py --in data/normalized_pt.csv --out data/classified_pt_v2.csv --country PT
python3 scripts/python/validate_gtin.py --in data/classified_pt_v2.csv --out data/validated_pt.csv
python3 scripts/python/build_unify_input.py --out data/_unify_manifest.json
python3 scripts/python/dedupe_unify.py --manifest data/_unify_manifest.json --out-csv data/unified_all.csv --dup-report data/duplicates_report.csv

# Phase 5
python3 scripts/python/export_artifacts.py --in data/unified_all.csv --outdir artifacts
```

## Validation
- `bash scripts/verify_phase5.sh` retorna 0
- ficheiros na pasta `artifacts/` existem e são não-vazios
