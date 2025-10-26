# Direct Execution Command — Phase 9 (100% Functional)

**Instruction to Codex (run this):** Execute **Runner 900** and its sub-runners 901–909 to deliver a 100% functional app.

Order:
1) 901 Ingest → 902 Normalize → 903 Classify → 904 Validate GTIN → 905 Dedupe & Unify → 906 Publish  
2) 907 GUI Completion & QA  
3) 908 Packaging & Launchers  
4) 909 CI wiring & Artifacts

Read SoT from:
- `docs/en/codex/architecture/app-status-index.json`
- `docs/en/codex/architecture/app-status2gpt.md`
- `docs/en/codex/architecture/policies.md`
- `docs/en/codex/architecture/sot.md`
- `docs/en/codex/architecture/data-model.md`
- `docs/en/codex/architecture/taxonomy.md`
- `docs/en/codex/progress.json`

Target outcomes:
- GUI FreeSimpleGUI completa (todas as ações operacionais).
- Pipeline end-to-end gera `artifacts/outputs/final.csv` e `final.sqlite`.
- Testes **pytest** a verde.
- Progresso Phase 9 atualizado (100%) e logs em `artifacts/logs/phase9_pipeline.log`.
