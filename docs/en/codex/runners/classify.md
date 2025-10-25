# Runner — Classify

**Goal:** Assign taxonomy  
**Idempotent:** Yes

## Inputs
- Previous step output
- Configurations from SoT

## Outputs
- Logs: `logs/classify.log`
- Artifacts: if applicable

## Command
```bash
bash scripts/steps/run_step.sh classify
```
