# Smart-Mode Policies (Full App)

## Option B — Codex First (sempre)
- O Codex/CI trabalha a partir do **branch `main`**. A aplicação local só é testada **depois**.
- O repositório deve ser atualizado pelo CI com **progresso** (`docs/en/codex/progress.json`) e **artefactos de log** em `artifacts/logs/`.

## Toolkit & Arquitetura
- **FreeSimpleGUI** é o único toolkit GUI.
- Backend em **Python 3.10+** com módulos por passo: `pipeline/ingest.py`, `normalize.py`, `classify.py`, `validate.py`, `dedupe.py`, `publish.py`.
- Interface de linha de comando para cada passo: `python -m pipeline.<step> --in ... --out ...`.
- Artefactos em `artifacts/inputs`, `artifacts/working`, `artifacts/outputs`, logs em `artifacts/logs`.

## Qualidade
- Testes unitários mínimos (`pytest`) por passo.
- Logging estruturado (CSV e txt) e mensagens de erro claras na GUI.
- Idempotência: correr o mesmo passo duas vezes não deve corromper saídas.
