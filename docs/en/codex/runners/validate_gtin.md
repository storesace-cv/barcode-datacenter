# Runner — Validate GTIN

**Goal:** Validate GTIN/EAN  
**Idempotent:** Yes

## Inputs
- Previous step output
- Configurations from SoT

## Outputs
- Logs: `logs/validate_gtin.log`
- Artifacts: if applicable

## Command
```bash
bash scripts/steps/run_step.sh validate_gtin
```
