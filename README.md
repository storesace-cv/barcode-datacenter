# barcode-datacenter

**Status:** Bootstrap (Phase 1) · **Date:** 2025-10-25  
**Scope:** Unified barcode/product catalogue for supermarkets in Portugal (PT), Angola (ANG) and Cabo Verde (CV).

This repository adopts **Smart‑Mode (ZThoteis style)**:
- Documentation-as-contract (Codex-first), idempotent runners, CI checks, and progress tracking.
- Strict folder conventions under `docs/en/codex/` for architecture, phases and runners.

## Source of Truth (SoT)
- [`docs/en/codex/architecture/sot.md`](docs/en/codex/architecture/sot.md)
- Progress index: [`docs/en/codex/progress.json`](docs/en/codex/progress.json)

## Quick start

```bash
# 0) clone and create your personal branch
git clone https://github.com/storesace-cv/barcode-datacenter.git
cd barcode-datacenter
git checkout -b my-barcode-datacenter

# 1) bootstrap env (idempotent)
bash scripts/bootstrap.sh

# 2) verify Phase 1 (bootstrap)
bash scripts/verify_phase1.sh

# 3) run a sample pipeline (OFF stub) - optional
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/python/extract_off_data.py --country PT --limit 200 --out data/off_sample_pt.jsonl
python scripts/python/normalize_products.py --in data/off_sample_pt.jsonl --out data/normalized_pt.csv --country PT
python scripts/python/classify_products.py --in data/normalized_pt.csv --out data/classified_pt.csv --country PT
python scripts/python/validate_gtin.py --in data/classified_pt.csv --out data/validated_pt.csv
```

## Roadmap (Phases)
See [`docs/en/codex/phases`](docs/en/codex/phases).

- **Phase 1 — Bootstrap & CI** (this commit)
- **Phase 2 — Ingestion (OFF + Retailers)**
- **Phase 3 — Normalisation & Classification (Family/Subfamily)**
- **Phase 4 — Validation (GTIN/GS1), Unification & Dedup**
- **Phase 5 — Publish (CSV/SQLite/JSONL) + Docs**

## Changelog
See [`CHANGELOG.md`](CHANGELOG.md).

---

© BWB — All rights reserved.



## Launcher (Smart-Mode)
Run: `bash scripts/launchers/launcher.sh` — backups, sync, venv, GUI start.  
_Updated: 2025-10-25_
