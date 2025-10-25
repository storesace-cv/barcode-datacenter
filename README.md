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

## Table of Contents
- [Overview](#overview)
- [Functional Layers](#functional-layers)
- [Smart-Mode Phases & Runners](#smart-mode-phases--runners)
- [Architecture Summary](#architecture-summary)
- [Data Model](#data-model)
- [Taxonomy](#taxonomy)
- [GUI Overview](#gui-overview)
- [Installation & Launcher](#installation--launcher)
- [Verification](#verification)
- [Workflows](#workflows)
- [Repository Structure](#repository-structure)
- [Roadmap Summary](#roadmap-summary)
- [License & Credits](#license--credits)

## Overview
Barcode Datacenter consolidates and classifies retail product data across **Portugal**, **Angola**, and **Cabo Verde**.
It provides a **unified taxonomy**, **GTIN validation**, **brand normalization** and **multi-format publication** (CSV/JSONL/SQLite),
with a **desktop GUI** (pywebview) and **Smart-Mode automation** (runners, verify scripts, CI).
Updated: 2025-10-25.

## Functional Layers
| Layer | Technology | Description |
|---|---|---|
| Backend | Python 3.11 · SQLite | Ingest, normalize, classify, validate GTIN, dedupe/unify, publish |
| Frontend | pywebview · HTML/JS/CSS | Desktop GUI (dashboard + actions) |
| Bridge | ExposedAPI (pywebview js_api) | Structured dicts across WebView boundary |
| Storage | SQLite · CSV · JSONL | Unified product store + artifacts |
| Automation | GitHub Actions · Smart-Mode scripts | CI, runners, phase verifications, release |
| Launcher | Bash (macOS bash 3.2) | Backup+sync from main, ensure venv, launch GUI |

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

> See Codex contracts in `docs/en/codex/runners/*.md` and phases in `docs/en/codex/phases/*.md`.

## Architecture Summary
See `docs/en/codex/architecture/sot.md` for SoT (source of truth).

## Data Model
See `docs/en/codex/architecture/data-model.md` for normalized fields.

## Taxonomy
See `docs/en/codex/architecture/taxonomy.md` for PT/ANG/CV families and subfamilies.

## GUI Overview
See `docs/en/README_GUI.md` for the pywebview bridge, UI structure and theming.

## Installation & Launcher
```bash
git clone https://github.com/storesace-cv/barcode-datacenter.git
cd barcode-datacenter
bash scripts/launchers/launcher.sh
```
Env:
- `PERSONAL_BRANCH` (default: `my-barcode-datacenter`)
- `PYTHON_BIN` (default: `python3`)
- `LAUNCH_NO_PULL=1` (offline start)

## Verification
```bash
bash scripts/verify_phase1.sh
bash scripts/verify_phase3.sh
bash scripts/verify_phase4.sh
bash scripts/verify_phase5.sh
bash scripts/verify_phase6.sh
bash scripts/verify_phase7.sh
bash scripts/verify_roadmap.sh
bash scripts/verify_ci_local.sh
```
## Workflows
- CI (`.github/workflows/ci.yml`) — manual `workflow_dispatch` available
- Phase 3 / Phase 4 / Phase 7 Launcher / Roadmap — manual dispatch
- Release Artifacts — manual tag or dispatch (`release.yml`)

## Repository Structure
```
docs/
  en/
    codex/
      architecture/
      phases/
      runners/
    roadmap.md
scripts/
  launchers/launcher.sh
  verify_phase*.sh
  verify_ci_local.sh
  ci_entrypoint.sh
data/
artifacts/
.github/workflows/
```

## Roadmap Summary
The live roadmap is maintained in `docs/en/roadmap.md`.

## License & Credits
MIT © 2025 — BWB · StoresAce CV.
