# Runner — Normalize

**Goal:** Normalize UOM/names  
**Idempotent:** Yes

## Inputs
- Previous step output
- Configurations from SoT

## Outputs
- Logs: `logs/normalize.log`
- Artifacts: if applicable

## Command
```bash
bash scripts/steps/run_step.sh normalize
```
