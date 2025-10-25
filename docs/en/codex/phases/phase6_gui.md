# Phase 6 — Desktop GUI (pywebview)

**Goal:** Provide a lightweight desktop shell with HTML/JS UI bridged to Python via pywebview.

## Deliverables
- `gui/` (index.html, app.js, style.css, dashboard.html)
- Backend bridge: `scripts/python/gui_backend.py`
- Verify script: `scripts/verify_phase6.sh`
- Runner: `docs/en/codex/runners/600.md`
- CI: `.github/workflows/gui.yml`

## Validation
- `bash scripts/verify_phase6.sh` returns 0
- `python scripts/python/gui_backend.py` launches a window (local)
