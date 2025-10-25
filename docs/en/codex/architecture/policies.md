# Smart-Mode Policies (Docs-Only Drop)

## Option B Only — Codex First
- Toda a execução é feita pelo Codex/CI a partir do **branch `main`**.
- Este bundle **não** contém código; apenas especificações e _runners_.
- O Codex deve **gerar/alterar código** para satisfazer os critérios de aceitação e **comitar de volta** ao repositório.
- O CI deve **escrever progresso** em `docs/en/codex/progress.json` e opcionalmente `artifacts/logs/*.log`.

## GUI Toolkit
- **FreeSimpleGUI** substitui qualquer uso anterior de PySimpleGUI.
- O Codex deve migrar imports e chamadas de API conforme necessário (nomes compatíveis).
