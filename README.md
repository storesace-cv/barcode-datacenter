# Barcode Datacenter — Smart-Mode

O Barcode Datacenter agrega códigos de barras e informação de produto de supermercados em Portugal, Angola e Cabo Verde, com fallback para fontes abertas. A aplicação fornece:

- **Coletores reais de supermercados** (Continente PT, Shoprite Angola, NosSuper Cabo Verde) com modo offline garantido e fallback para Open Food Facts.
- **Pipeline Smart-Mode completo** com orquestrador reutilizável, logs estruturados e artefactos finais (CSV, JSONL, SQLite).
- **Interface GUI e web backend** com workflow step-by-step, estado em tempo real e arranque manual de cada etapa.
- **Documentação Codex/SoT** atualizada para acompanhamento de fases e execução idempotente.

## Requisitos

- Python 3.11+
- Dependências listadas em `requirements.txt`
- Acesso à internet apenas se desejar recolha online (por omissão o pipeline pode correr em modo offline com fixtures incluídas).

## Execução rápida

```bash
# Instalar dependências
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Executar pipeline completo usando apenas fixtures offline
python -m pipeline.run --offline

# Executar pipeline completo com tentativa de recolha online prioritária
python -m pipeline.run --limit 90 --country PT --country ANG --country CV
```

### Artefactos gerados

Após a execução serão criados ficheiros em `artifacts/`:

- `working/ingested.csv` — dados crus por conector, com proveniência detalhada.
- `working/unified.csv` — dataset deduplicado e enriquecido.
- `outputs/final.csv`, `final.jsonl`, `final.sqlite` — artefactos finais prontos a consumir.
- `logs/` — registos estruturados para cada passo (`phase9_pipeline.log`, `gui_actions.log`).
- `logs/app_full_logs.txt` — diário exaustivo (opcional) quando o modo de depuração está ativo.

### Logging exaustivo para depuração

Para capturar absolutamente tudo o que a aplicação faz (stdout, stderr, exceções não tratadas e entradas estruturadas), ative o modo de depuração ao lançar a GUI:

```bash
scripts/launchers/launch_gui.sh --debug-on
```

Enquanto o modo estiver ativo, a variável de ambiente `APP_FULL_LOGGING=1` é propagada para os processos Python e o ficheiro `logs/app_full_logs.txt` recebe toda a atividade da aplicação, incluindo métricas do pipeline e mensagens de erro. Utilize `--debug-off` (ou omita a flag) para iniciar a aplicação no modo normal.

## Coletores e estratégia de dados

| Fonte | Países | Prioridade | Notas |
|-------|--------|------------|-------|
| Continente | PT | Alta | API JSON (quando disponível) com fallback offline garantido. |
| Shoprite | Angola | Alta | Scraper JSON com fallback offline garantido. |
| NosSuper | Cabo Verde | Alta | Scraper JSON com fallback offline garantido. |
| Open Food Facts | PT/ANG/CV | Média | Apenas utilizado quando supermercados não respondem. |

- A ingestão guarda métricas por origem, modo (online/offline) e país, além de proveniência detalhada por linha.
- O modo offline pode ser forçado com `--offline` ou pelo toggle na interface GUI.

## Orquestração programática

A classe `pipeline.orchestrator.SmartPipelineRunner` expõe cada etapa como `StepResult` reutilizável:

```python
from pipeline.orchestrator import SmartPipelineRunner

runner = SmartPipelineRunner()
runner.run_step('ingest', limit=60, prefer_online=False)
runner.run_all(overrides={'ingest': {'countries': ('PT',)}})
status = runner.status()
```

Cada `StepResult` inclui `metrics`, `artifacts` e `logs` prontos para utilização pelo backend e pela GUI.

## GUI / Backend

```bash
# Arrancar o backend HTTP + GUI
python scripts/python/gui_backend.py
```

- `http://127.0.0.1:6754/index.html` apresenta o workflow orientado por passos.
- Botões dedicados permitem executar cada etapa na ordem correta ou o pipeline completo.
- O painel de estado mostra métricas agregadas e lista de artefactos atualizada.
- O toggle “Forçar ingestão offline” aplica-se quer a execuções isoladas quer ao pipeline completo.

## Estrutura dos módulos

```
pipeline/
  ingest.py            # Gestão de conectores, proveniência e métricas
  normalize.py         # Normalização de quantidades, países, moedas
  classify.py          # Taxonomia (família/subfamília)
  validate.py          # Validação de GTIN
  dedupe.py            # Fusão com pontuação por fonte
  publish.py           # Exportação final
  orchestrator.py      # Runner reutilizável e estado do pipeline
```

## Testes

```bash
pytest
```

Os testes cobrem ingestão offline, deduplicação e execução end-to-end garantindo que os artefactos finais e logs são gerados corretamente.

## Documentação adicional

Consulte `docs/en/` para detalhes Codex/SoT, runners e progresso. Atualizações relevantes encontram-se em `CHANGELOG.md`.
