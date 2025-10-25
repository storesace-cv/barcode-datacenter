# Runner — Dedupe & Unify

**Goal:** Detect and unify duplicates  
**Idempotent:** Yes

## Inputs
- Previous step output
- Configurations from SoT

## Outputs
- Logs: `logs/dedupe_unify.log`
- Artifacts: if applicable

## Command
```bash
bash scripts/steps/run_step.sh dedupe_unify
```
