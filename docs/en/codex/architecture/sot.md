# Source of Truth (SoT)

**Project:** barcode-datacenter  
**Updated:** 2025-10-25

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

## Phase 6 — Desktop GUI (pywebview)

**Status:** ✅ Ready · **Date:** 2025-10-25  
**Owner:** Codex Executor (Smart-Mode)  
**Objective:** Provide a lightweight desktop shell with HTML/JS UI bridged to Python via pywebview, enabling interactive catalog exploration, classification review, and reporting.

**Deliverables**
| Component | Path | Description |
|------------|------|-------------|
| Backend Bridge | `scripts/python/gui_backend.py` | Exposes operational methods to JS via pywebview |
| Frontend Shell | `gui/index.html`, `gui/app.js`, `gui/style.css`, `gui/dashboard.html` | Declarative UI built with native JS/CSS |
| Persistence | `data/barcode_gui.db` | SQLite storage for logs and cache |
| Validation | `scripts/verify_phase6.sh` | Ensures GUI files + backend compile |
| CI | `.github/workflows/gui.yml` | GitHub Actions workflow verifying GUI integrity |
| Runner | `docs/en/codex/runners/600.md` | Launches GUI |

**Dependencies**
- Python ≥ 3.11  
- `pywebview ≥ 4.4`  
- `sqlite3` (standard library)

**Verification**
```bash
bash scripts/verify_phase6.sh
```

**Execution**
```bash
python scripts/python/gui_backend.py
```

**Outputs**
- GUI window (1200×800) with embedded dashboard
- SQLite log entries (`logs` table)



## Phase 7 — Launcher (Smart-Mode)

**Status:** ✅ Ready · **Date:** 2025-10-25

**Artifacts**
- `scripts/launchers/launcher.sh`
- `docs/en/codex/runners/700_launcher.md`
- `scripts/verify_launcher.sh`
- `.github/workflows/phase7_launcher.yml`
