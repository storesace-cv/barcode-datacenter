# Source of Truth (SoT)

Defines the canonical flow of the Barcode Datacenter Smart-Mode pipeline.

1. **Ingest** — import source data (CSV/JSONL).
2. **Normalize** — clean and normalize naming/UOM.
3. **Classify** — assign taxonomy PT·ANG·CV.
4. **Validate GTIN** — check GTIN integrity.
5. **Dedupe & Unify** — merge canonical items.
6. **Publish** — export final artifacts (CSV/JSONL/SQLite).
