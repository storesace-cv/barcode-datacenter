# Changelog

## 2025-10-25
- Phase 1 bootstrap created: docs, runners, scripts, CI, tests, seed taxonomy.
- Stubbed Phase 6 dashboard scaffolding: backend loaders, GUI layout, deterministic seed data.


## 2025-10-26
- Substituído o gerador stub por conectores de supermercados com fallback offline.
- Criado orquestrador `SmartPipelineRunner` e expostos `StepResult` em cada módulo.
- Backend HTTP/GUI atualizados para workflow step-by-step com estado em tempo real.
- Documentação (README, Codex) atualizada para refletir arquitetura e execução.

## v0.1.0
- First public artifacts (CSV/JSONL/SQLite)



## [2025-10-25] phase6.1 — Launcher venv enforcement
- Launcher now guarantees GUI execution inside `.venv`
- Added `scripts/verify_venv_launcher.sh` and workflow `.github/workflows/launcher.yml`
- Codex updated: `docs/en/codex/runners/620.md`
