# Phase 2 — Ingestion (OFF + Retailers)

**Goal:** Fetch product data from Open Food Facts and retailer catalogues (where legal).

## Runners
- `200` OFF ingestion
- `210` Retailer ingestion (per-country stubs)

## Validation
- OFF sample JSONL exists for PT and optionally ANG/CV
- Each ingestion script idempotent (same command, same output hash)
