# Source of Truth (SoT)

**Project:** barcode-datacenter  
**Date:** 2025-10-25

## Goals
- Build a unified product catalogue for PT/ANG/CV with EAN/GTIN, brand, name, family/subfamily, provenance and (optional) price.
- Provide reproducible pipelines with CI verification and progress tracking.

## Entities
- **Product**: `gtin`, `name`, `brand`, `qty`, `uom`, `country`, `source`, `url`, `currency`, `price` (optional), `category_raw`
- **Classification**: `family`, `subfamily` (normalized)
- **Audit**: `ingested_at`, `normalized_at`, `classified_at`, `hash_id`

## Constraints
- Idempotent operations; re-running must not duplicate rows.
- Prefer EAN/GTIN as primary key; fallback join on normalized name+brand+qty.
- Country in {PT, ANG, CV}; Currency in {EUR, AOA, CVE}.
