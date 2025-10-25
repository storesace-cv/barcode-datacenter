# Phase 3 — Normalisation & Classification (Family/Subfamily)

**Status:** ready · **Updated:** 2025-10-25

**Goal:** Normalize attributes and classify products into **FAMILY/SUBFAMILY** for PT/ANG/CV using deterministic dictionaries first and heuristics second.

## Inputs
- Normalized CSV from Phase 2/300: `gtin,name,brand,qty,uom,country,source,url,price,currency,category_raw,family,subfamily`
- Dictionaries under `data/seed/dictionaries/`

## Dictionaries
- `synonyms_uom.csv` — Normalize units (e.g., LITRO→L)
- `brands_normalization.csv` — Canonical brand names (e.g., "COCA COLA"→"COCA-COLA")
- `family_rules.csv` — Keyword→FAMILY mapping per country
- `subfamily_rules.csv` — Keyword→SUBFAMILY mapping per FAMILY and country
- `country_localizations.csv` — Country code normalization

> All CSVs are ASCII/UPPERCASE, `;`-separated and without BOM.

## Runners
- `315` — Load dictionaries (noop check)
- `320` — Classify Products v2 (dict-first + heuristics)

## Commands
```bash
# Produce a small normalized sample (offline stub from OFF)
python scripts/python/extract_off_data.py --country PT --limit 50 --out data/off_pt_stub.jsonl
python scripts/python/normalize_products.py --in data/off_pt_stub.jsonl --out data/normalized_pt.csv --country PT

# Run dictionary-based classification v2
python scripts/python/classify_products_v2.py --in data/normalized_pt.csv --out data/classified_pt_v2.csv --country PT

# Verify Phase 3 end-to-end
bash scripts/verify_phase3.sh
```

## Validation
- `verify_phase3.sh` returns 0
- `UNMAPPED` rate ≤ 30% on stub input (dict grows over time)
- Deterministic outputs across runs (idempotent)
