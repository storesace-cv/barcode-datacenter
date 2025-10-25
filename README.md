<div align="center">
  <h1>barcode-datacenter</h1>
  <p><em>PT · ANG · CV unified barcode & product taxonomy — Smart-Mode powered</em></p>
  <p>
    <img alt="Smart-Mode" src="https://img.shields.io/badge/Smart--Mode-enabled-4C9A2A">
    <img alt="Codex" src="https://img.shields.io/badge/Codex-contract--docs-blue">
    <img alt="CI" src="https://img.shields.io/badge/CI-GitHub%20Actions-lightgrey">
    <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
  </p>
</div>

---

## Overview
Barcode Datacenter consolidates and classifies retail product data across **Portugal**, **Angola**, and **Cabo Verde**.
It provides a unified taxonomy, GTIN validation, brand normalization and multi-format publication (CSV/JSONL/SQLite), with a desktop GUI (pywebview) and Smart-Mode automation (runners, verify scripts, CI).

**Live roadmap:** See docs/en/roadmap.md for the live roadmap.

---

## Functional Layers
| Layer | Technology | Description |
|---|---|---|
| Backend | Python 3.11 · SQLite | Ingest, normalize, classify, validate GTIN, dedupe/unify, publish |
| Frontend | pywebview · HTML/JS/CSS | Desktop GUI (dashboard + actions) |
| Bridge | ExposedAPI (pywebview js_api) | Structured dicts across WebView boundary |
| Storage | SQLite · CSV · JSONL | Unified product store + artifacts |
| Automation | GitHub Actions · Smart-Mode scripts | CI, runners, phase verifications, release |
| Launcher | Bash (macOS bash 3.2) | Backup+sync from main, ensure venv, launch GUI |

---

## Smart-Mode Phases & Runners
| Phase | Name | Key Deliverables | Runners |
|---:|---|---|---|
| 1 | Bootstrap | Repo skeleton, SoT, CI bootstrap | 100–110 |
| 2 | Ingest & Normalize | OFF stub, normalize schema (CSV) | 200–210 |
| 3 | Classify | Dict-first classifier (brand/uom/family) | 300–320 |
| 4 | Validation & Unify | GTIN validate, dedupe & unify, dup report | 400–420 |
| 5 | Publish | CSV / JSONL / SQLite artifacts | 500 |
| 6 | Desktop GUI | pywebview shell + dashboard | 600 |
| 7 | Launcher | Backup+sync main→branch + GUI launcher | 700 |

> Use the docs/en/codex/runners/*.md files as Codex contracts for automation.

---

## Architecture Summary (from SoT)
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
- SQLite l

…

---

## Data Model (normalized)
# Data Model

## Input (examples)
- JSONL from OFF (`code`, `product_name`, `brands`, `quantity`, `categories`, `countries`, `url`)
- Retailer HTML/JSON (structure varies)

## Normalized Schema (CSV)
`gtin,name,brand,qty,uom,country,source,url,price,currency,category_raw,family,subfamily`

- `qty` numeric; `uom` normalized (G, KG, ML, L, UN).
- `family/subfamily` empty before classification; then filled by classifier.

---

## Taxonomy (PT · ANG · CV)
# Taxonomy Design (Family/Subfamily)

This taxonomy serves Portugal (PT), Angola (ANG) and Cabo Verde (CV). It follows a pragmatic mapping:
- Base layer inspired by GS1/GPC families (high-level).
- Retailer categories are mapped via heuristics to these families/subfamilies.
- OFF categories are used as a fallback when retailer mapping is absent.

Seed CSVs are in `data/seed/*.csv`. Extend by appending rows. Keep names UPPERCASE and ASCII-only for determinism.

---

## GUI (pywebview) Overview
This folder hosts architecture docs for the GUI layer (pywebview).

---

## Installation & Launcher
```bash
git clone https://github.com/storesace-cv/barcode-datacenter.git
cd barcode-datacenter
bash scripts/launchers/launcher.sh
```
**Env vars:** PERSONAL_BRANCH (default: my-barcode-datacenter), PYTHON_BIN (default: python3), LAUNCH_NO_PULL=1 (offline).

---

## Verification Commands
- bash scripts/verify_phase1.sh — bootstrap
- bash scripts/verify_phase3.sh — classify v2 (dicts)
- bash scripts/verify_phase4.sh — unify & duplicates
- bash scripts/verify_phase5.sh — publish artifacts
- bash scripts/verify_phase6.sh — GUI checks
- bash scripts/verify_phase7.sh — launcher checks
- bash scripts/verify_roadmap.sh — roadmap presence
- bash scripts/verify_ci_local.sh — local CI simulation

---

## Workflows
- CI (manual: Actions → CI → Run workflow)
- Phase 3 / Phase 4 / Phase 7 Launcher / Roadmap (workflow_dispatch)
- Release Artifacts (manual tag or dispatch)

---

## Repository Structure (abridged)
```
docs/
  en/
    codex/
      architecture/
      phases/
      runners/
    roadmap.md
scripts/
  python/
  verify_phase*.sh
  launchers/launcher.sh
data/
artifacts/
.github/workflows/
```

---

## License & Credits
MIT © 2025 — BWB · StoresAce CV.
Smart-Mode and Codex integration by design.


## Roadmap Summary
The live roadmap is maintained in docs/en/roadmap.md.
