# Runner — Ingest

**Goal:** Import source CSV/JSONL  
**Idempotent:** Yes

## Inputs
- Previous step output
- Configurations from SoT

## Outputs
- Logs: `logs/ingest.log`
- Artifacts: if applicable

## Command
```bash
bash scripts/steps/run_step.sh ingest
```
