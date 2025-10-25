# App Status — GPT Brief (SoT)

## Phase 7 — Smart-Mode GUI wiring & pipeline stub
**Goal:** Wire the existing FreeSimpleGUI GUI to a Smart-Mode pipeline stub so that pressing **“Run pipeline (Smart-Mode)”** executes a no-op pipeline, logs to `artifacts/logs/phase7_pipeline.log`, and updates `docs/en/codex/progress.json`.

### Execution Policy
**We ALWAYS use Option B:** Codex-first execution. Push/merge to `main`, wait for Codex to finish, then pull `main` and only then test locally.

### Deliverables
1. Runner: `docs/en/codex/runners/700.md`.
2. Pipeline stub: `scripts/codex/run_smart_pipeline.py`.
3. Progress helper: `scripts/codex/progress_helper.py`.
4. GUI integration: `app/gui/gui_app.py` calls the pipeline stub.
5. Verifier: `scripts/verify_phase7_status.sh`.
6. CI: `.github/workflows/phase7.yml`.
7. Option-B helpers: `scripts/smartmode_optionB_apply_and_push.sh`, `scripts/codex/wait_codex_and_pull.sh`.

### Acceptance (high-level)
- Codex reads runner 700 from `main` and executes.
- After Codex completes, `docs/en/codex/progress.json` shows phase 7 task `gui_wiring` >= 100 and `artifacts/logs/phase7_pipeline.log` exists in the repo.
- Local machine pulls `main` and only then runs GUI smoke test.
