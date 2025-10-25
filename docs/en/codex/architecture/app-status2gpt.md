# App Status — GPT Brief (SoT)

## Phase 7 — Smart-Mode GUI wiring & pipeline stub
(unchanged) — Escopo mínimo: janela simples com botão **Run pipeline (Smart-Mode)** e **Exit**.

## Phase 8 — FreeSimpleGUI Dashboard (Smart-Mode)
**Objetivo:** Evoluir a GUI de uma janela simples para um **dashboard completo** semelhante ao *Screenshot 2025‑10‑25 at 18.50.37.png*, usando **FreeSimpleGUI**.

### Requisitos de Layout (ver também runner 800.md)
- **Janela**: título “Barcode Datacenter GUI”, tema escuro.
- **Sidebar (Workflow)** com botões verticais (ordem):  
  `Dashboard`, `Ingest`, `Normalize`, `Classify`, `Validate GTIN`, `Dedupe & Unify`, `Publish`;  
  seção **Tools / Logs**; linha com `Branch: <nome-do-branch>`.
- **Header (top-right)**: botões `Sync Main`, `Refresh`, `Open Dashboard` (abrir URL local/placeholder).
- **Painel Status** (multi-linha readonly) exibindo JSON com chaves: `ok`, `ts`, `root`, `branch`, `version`.
- **Painel Actions** com:  
  - Dropdown “Run step” (valores: `Ingest`, `Normalize`, `Classify`, `Validate GTIN`, `Dedupe & Unify`, `Publish`) + botão `Run`  
  - Botão **Run pipeline (Smart-Mode)**  
  - Botões `Open artifacts dir`, `Open logs`
- **Tabs** centrais: `Data Table`, `Preview / Artifacts`, `Logs` (conteúdo placeholder).
- **Status Bar** inferior: `Ready` e contadores à direita `Valid: 0  Invalid: 0  Duplicates: 0  Unified: 0`.

### Comportamento / Ligações
- **Sem lógica de pipeline nova** nesta fase — reaproveitar o stub existente para o botão **Run pipeline (Smart-Mode)**.
- Botões `Open artifacts dir` / `Open logs` devem abrir/mostrar diretório `artifacts/` (placeholder aceitável).
- `Sync Main` deve executar o `git pull --ff-only` do branch atual e informar no painel de logs (placeholder aceitável no CI).
- `Refresh` deve recarregar o painel `Status` com JSON atual (timestamp, path raiz, branch detectado, versão `v0.1.0`).

### Compatibilidade
- Migrar de PySimpleGUI para **FreeSimpleGUI** (imports/nomes).

### Entregáveis
- Código da GUI atualizado (implementado pelo Codex).  
- Atualização dos scripts de verificação (grep estático e _smoke checks_).  
- Progresso (`phase 8`) reportado no `progress.json`.
