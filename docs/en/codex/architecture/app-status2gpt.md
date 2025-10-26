# App Status — GPT Brief (SoT)

## Objetivo da Phase 9
Tornar a aplicação **100% funcional**: todos os botões e etapas do pipeline operacionais, do *Ingest* ao *Publish*, com GUI FreeSimpleGUI completa, logging, verificação de erros, e artefactos finais exportados.

## Pipeline (SoT)
Ver `docs/en/codex/architecture/sot.md` para a sequência: Ingest → Normalize → Classify → Validate GTIN → Dedupe & Unify → Publish.

## Requisitos funcionais (GUI + Backend)
1. **GUI (FreeSimpleGUI)** com todas as vistas, cabeçalho, sidebar, tabs e ações operacionais (ver Phase 8).
2. **Ligação GUI ↔ Backend**: cada botão dispara o respetivo módulo real e escreve artefactos em `artifacts/...`.
3. **Backend (módulos)**: `pipeline/ingest.py`, `normalize.py`, `classify.py`, `validate.py`, `dedupe.py`, `publish.py` com `main(args)` + CLI `argparse`.
4. **Logs e artefactos**: logs por passo + `phase9_pipeline.log`; artefactos finais `final.csv` e `final.sqlite`.
5. **Erros e robustez**: sem crashes; mensagens claras; status `ok=false` quando houver erro.
6. **Testes**: `pytest -q` com seed mínima; CI corre testes e mini-pipeline.

## Entregáveis
- Código completo da GUI e backend + artefactos finais; progresso Phase 9 atualizado.
