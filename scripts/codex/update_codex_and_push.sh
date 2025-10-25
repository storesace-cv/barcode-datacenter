#!/usr/bin/env bash
set -euo pipefail
SUMMARY="${1:-pipeline}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
BRANCH="${PERSONAL_BRANCH:-my-barcode-datacenter}"
TS="$(date -u +%FT%TZ)"
echo "- ${TS} — ${SUMMARY} ok (smart-mode)" >> docs/en/codex/STATUS.md
git add docs/en/codex/STATUS.md artifacts || true
git commit -m "codex:ok:${SUMMARY} ts=${TS}" || true
git push origin "$BRANCH" || true
