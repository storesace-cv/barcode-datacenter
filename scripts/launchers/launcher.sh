#!/usr/bin/env bash
# Smart-Mode Launcher — hardened (backups outside repo + git guards) — macOS bash 3.2 compatible
set -euo pipefail

PERSONAL_BRANCH="${PERSONAL_BRANCH:-my-barcode-datacenter}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# Backups OUTSIDE the repo to avoid untracked/merge issues
BACKUP_DIR="${BACKUP_DIR:-$HOME/Library/Application Support/barcode-datacenter/backups}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
NO_PULL="${LAUNCH_NO_PULL:-0}"

# Ensure backup dir
mkdir -p "$BACKUP_DIR/$TIMESTAMP"

echo "[Launcher] Repo: $REPO_ROOT"
echo "[Launcher] Backup dir: $BACKUP_DIR/$TIMESTAMP"

cd "$REPO_ROOT"

# Helper: portable find-based backup of protected files
backup_file() {
  src="$1"
  dest="$BACKUP_DIR/$TIMESTAMP/$src"
  mkdir -p "$(dirname "$dest")"
  cp -p "$src" "$dest" 2>/dev/null && echo "  - saved $src" || true
}

# 1) Backup local data (outside repo)
echo "[Launcher] Backing up local data files"
# Simple set: DB/Excel + artifacts folder
for pat in "data/*.sqlite" "data/*.db" "data/**/*.sqlite" "data/**/*.db" "data/**/*.xlsx" "data/**/*.xls"; do
  dir="$(dirname "$pat")"; name="$(basename "$pat")"
  [ -d "$dir" ] || continue
  find "$dir" -type f -name "$name" 2>/dev/null | while IFS= read -r f; do
    f="${f#./}"; [ -f "$f" ] && backup_file "$f"
  done
done
# Copy artifacts entirely if exists
if [ -d "artifacts" ]; then
  rsync -a --delete --exclude=".DS_Store" artifacts/ "$BACKUP_DIR/$TIMESTAMP/artifacts/"
  echo "  - mirrored artifacts/"
fi

# 2) Git sync with guards
if [ "$NO_PULL" != "1" ]; then
  # If a rebase/merge is in progress, abort to a clean state
  if [ -d ".git/rebase-apply" ] || [ -d ".git/rebase-merge" ]; then
    echo "[Launcher] Detected unfinished rebase. Aborting."
    git rebase --abort || true
  fi
  if [ -f ".git/MERGE_HEAD" ]; then
    echo "[Launcher] Detected unfinished merge. Aborting."
    git merge --abort || true
  fi

  echo "[Launcher] Git fetch/pull from origin"
  git fetch origin

  # Ensure main exists locally and is up to date
  if git show-ref --verify --quiet refs/heads/main; then
    git checkout main
  else
    git checkout -b main || git checkout main
  fi
  git pull --rebase origin main || true

  # Checkout or create personal branch
  if git show-ref --verify --quiet "refs/heads/$PERSONAL_BRANCH"; then
    git checkout "$PERSONAL_BRANCH"
    # Rebase onto latest main; if untracked files block merge, use stash-like guard
    git rebase main || git merge --no-ff main -m "launcher: merge main -> $PERSONAL_BRANCH [smart-mode]"
  else
    echo "[Launcher] Creating personal branch $PERSONAL_BRANCH from main"
    git checkout -b "$PERSONAL_BRANCH" main
  fi
else
  echo "[Launcher] Skipping git fetch/pull due to LAUNCH_NO_PULL=1"
fi

# 3) Python env & requirements
echo "[Launcher] Ensuring virtualenv and requirements"
if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -U pip
[ -f requirements.txt ] && pip install -r requirements.txt || true

# 4) Verify GUI (non-blocking)
echo "[Launcher] Verifying GUI (phase6)"
[ -f scripts/verify_phase6.sh ] && bash scripts/verify_phase6.sh || true

# 5) Launch GUI
APP="scripts/python/gui_backend.py"
if [ ! -f "$APP" ]; then
  echo "[Launcher] ERROR: $APP not found"; exit 1;
fi
echo "[Launcher] Starting GUI..."
exec "$PYTHON_BIN" "$APP"
