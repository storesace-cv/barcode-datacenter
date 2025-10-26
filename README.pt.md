# Barcode Datacenter — Visão Geral

O projecto consolida informação de produtos e códigos de barras com foco em Portugal, Angola e Cabo Verde. A versão atual privilegia fontes de supermercados, mantendo fallback controlado para dados comunitários.

## Principais componentes

- **Ingestão com conectores de supermercados** (Continente, Shoprite Angola, NosSuper) com fallback opcional para Open Food Facts.
- **Pipeline Smart-Mode** com etapas `ingest → normalize → classify → validate → dedupe → publish` orquestradas por `SmartPipelineRunner`.
- **Interface gráfica** com modo step-by-step e backend HTTP que expõe estado, artefactos e execução de cada passo.
- **Artefactos finais** em CSV, JSON Lines e SQLite, prontos para integração externa.

## Como executar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Modo offline (usa fixtures incluídas)
python -m pipeline.run --offline

# Modo online (tenta recolha real antes de recorrer ao fallback)
python -m pipeline.run --limit 90 --country PT --country ANG --country CV
```

## GUI

```bash
python scripts/python/gui_backend.py
# abrir http://127.0.0.1:6754/index.html
```

Na interface é possível:

- Seguir o fluxo lógico passo-a-passo com feedback visual.
- Forçar ingestão offline através de um toggle dedicado.
- Consultar artefactos e logs em tempo real.

## Dados gerados

- `artifacts/working/ingested.csv` — fonte original + proveniência por conector.
- `artifacts/working/unified.csv` — dataset deduplicado com métricas de confiança.
- `artifacts/outputs/final.*` — ficheiros finais para downstream (CSV/JSONL/SQLite).
- `artifacts/logs/*.log` — registos estruturados do pipeline e da GUI.

## Extensões futuras

- Novos conectores (Mercadão PT, Candando Angola, retalhistas independentes CV).
- Visualizações dedicadas na GUI (gráficos de stocks/preços, auditoria de duplicados).
- Publicação incremental com histórico temporal em vez de substituição completa.
