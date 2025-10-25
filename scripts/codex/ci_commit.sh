#!/usr/bin/env bash
set -euo pipefail

BRANCH="${GITHUB_HEAD_REF:-${GITHUB_REF_NAME:-}}"
if [ -z "${BRANCH}" ]; then
  BRANCH="$(echo "${GITHUB_REF:-}" | sed -E 's|^refs/heads/||')"
fi
[ -z "${BRANCH}" ] && BRANCH="main"

git config user.name  "codex-bot"
git config user.email "codex-bot@users.noreply.github.com"

# Executa o stub (gera log e atualiza gui_wiring)
python3 scripts/codex/run_smart_pipeline.py || true

# Marca a tarefa de commit do CI como concluída
python3 scripts/codex/progress_helper.py \
  --phase 7 --task ci_commit --value 100 \
  --msg "CI wrote progress/logs back to repo."

# Comita e faz push das alterações (progress.json + log)
mkdir -p artifacts/logs || true
git add docs/en/codex/progress.json artifacts/logs/phase7_pipeline.log || true

if git diff --cached --quiet; then
  echo "No changes to commit."
  exit 0
fi

git commit -m "codex: phase7 progress/logs update [skip ci]" || true
git push origin "${BRANCH}"
