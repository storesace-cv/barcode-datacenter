# Phase 4 — Validation (GTIN/GS1), Unification & Dedup

**Status:** ready · **Updated:** 2025-10-25

**Goal:** Validar GTIN, consolidar registos duplicados (por GTIN ou chave canónica) e produzir um dataset **unificado** + **relatório de duplicados** para QA.

## Inputs
- `data/normalized_*.csv` (Phase 2/3)
- `data/classified_*[v2].csv` (Phase 3)

## Outputs
- `data/validated_*.csv` — acrescenta coluna `gtin_valid` (0/1) *(já suportado por runner 400)*
- `data/unified_all.csv` — conjunto unificado (PT/ANG/CV), sem duplicados
- `data/duplicates_report.csv` — detalhe de colisões/mesclas

## Runners
- `400` — Validate GTIN (já existente)
- `410` — Build Unification Input (auto-descoberta dos CSVs válidos)
- `420` — Dedup & Unify → `unified_all.csv` + `duplicates_report.csv`

## Comandos
```bash
# 1) Preparação (stub OFF → normalize → classify v2 → validate)
python3 scripts/python/extract_off_data.py --country PT --limit 60 --out data/off_pt.jsonl
python3 scripts/python/normalize_products.py --in data/off_pt.jsonl --out data/normalized_pt.csv --country PT
python3 scripts/python/classify_products_v2.py --in data/normalized_pt.csv --out data/classified_pt_v2.csv --country PT
python3 scripts/python/validate_gtin.py --in data/classified_pt_v2.csv --out data/validated_pt.csv

# 2) Phase 4
python3 scripts/python/build_unify_input.py --out data/_unify_manifest.json
python3 scripts/python/dedupe_unify.py --manifest data/_unify_manifest.json --out-csv data/unified_all.csv --dup-report data/duplicates_report.csv
```

## Validation
- `bash scripts/verify_phase4.sh` retorna 0
- `unified_all.csv` existe e contém ≥ 1 linha de dados
- `duplicates_report.csv` existe e contém as colisões identificadas
