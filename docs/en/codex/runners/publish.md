# Runner — Publish

**Goal:** Export final artifacts  
**Idempotent:** Yes

## Inputs
- Previous step output
- Configurations from SoT

## Outputs
- Logs: `logs/publish.log`
- Artifacts: if applicable

## Command
```bash
bash scripts/steps/run_step.sh publish
```
