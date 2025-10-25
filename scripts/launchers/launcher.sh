#!/usr/bin/env bash
# Smart-Mode Launcher (macOS bash 3.2 compatible; no 'globstar')
set -euo pipefail

PERSONAL_BRANCH="${PERSONAL_BRANCH:-my-barcode-datacenter}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKUP_DIR="$REPO_ROOT/.local_backup"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
NO_PULL="${LAUNCH_NO_PULL:-0}"

# Protected patterns (newline-separated for bash 3.2)
read -r -d '' PROTECT_PATTERNS <<'EOF' || true
data/*.sqlite
data/*.db
data/**/.keep  # placeholder to allow recursive find
data/**/*.sqlite
data/**/*.db
data/**/*.xlsx
data/**/*.xls
artifacts/**
EOF

echo "[Launcher] Repo: $REPO_ROOT"
cd "$REPO_ROOT"
mkdir -p "$BACKUP_DIR/$TIMESTAMP"

# Helper: copy preserving structure
backup_file() {
  src="$1"
  dest="$BACKUP_DIR/$TIMESTAMP/$src"
  mkdir -p "$(dirname "$dest")"
  cp -p "$src" "$dest" 2>/dev/null && echo "  - saved $src" || true
}

restore_file() {
  rel="$1"
  src="$BACKUP_DIR/$TIMESTAMP/$rel"
  if [ -f "$src" ] && [ ! -f "$rel" ]; then
    mkdir -p "$(dirname "$rel")"
    cp -p "$src" "$rel" && echo "  - restored $rel"
  fi
}

# 1) Backup local files (find instead of globstar)
echo "[Launcher] Backing up local data files to $BACKUP_DIR/$TIMESTAMP"
# Expand patterns using find
echo "$PROTECT_PATTERNS" | while IFS= read -r pat; do
  # skip comments/empty
  case "$pat" in ''|\#*|*'.keep'*) continue;; esac
  # translate ** to a broad find; handle artifacts/** specially
  if echo "$pat" | grep -q '\*\*'; then
    base="${pat%%/**}"
    suffix="${pat##*/**/}"
    [ -z "$suffix" ] && suffix="*"
    find "$base" -type f -name "$suffix" 2>/dev/null | while IFS= read -r f; do
      # normalize leading ./
      f="${f#./}"
      [ -f "$f" ] && backup_file "$f"
    done
  else
    # simple pattern: use find on dirname and -name on basename
    dir="$(dirname "$pat")"
    name="$(basename "$pat")"
    [ -d "$dir" ] || continue
    find "$dir" -maxdepth 1 -type f -name "$name" 2>/dev/null | while IFS= read -r f; do
      f="${f#./}"
      [ -f "$f" ] && backup_file "$f"
    done
  fi
done

# 2) Git sync (main is SoT)
if [ "$NO_PULL" != "1" ]; then
  echo "[Launcher] Git fetch/pull from origin"
  git fetch origin
  if git show-ref --verify --quiet refs/heads/main; then
    git checkout main
  else
    git checkout -b main || git checkout main
  fi
  git pull --rebase origin main || true
else
  echo "[Launcher] Skipping git fetch/pull due to LAUNCH_NO_PULL=1"
fi

# Ensure personal branch exists and is updated
if git show-ref --verify --quiet "refs/heads/$PERSONAL_BRANCH"; then
  git checkout "$PERSONAL_BRANCH"
  if [ "$NO_PULL" != "1" ] && git show-ref --verify --quiet refs/heads/main; then
    git rebase main || git merge --no-ff main -m "launcher: merge main -> $PERSONAL_BRANCH [smart-mode]"
  fi
else
  echo "[Launcher] Creating personal branch $PERSONAL_BRANCH from main"
  git checkout -b "$PERSONAL_BRANCH" main
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

# 4) Verify GUI
echo "[Launcher] Verifying GUI (phase6)"
[ -f scripts/verify_phase6.sh ] && bash scripts/verify_phase6.sh || true

# 5) Restore protected files if missing
echo "[Launcher] Restoring protected files if necessary"
# Walk backup tree and restore missing counterparts
if [ -d "$BACKUP_DIR/$TIMESTAMP" ]; then
  (cd "$BACKUP_DIR/$TIMESTAMP" && find . -type f | sed 's#^\./##') | while IFS= read -r rel; do
    restore_file "$rel"
  done
fi

# 6) Launch GUI
APP="scripts/python/gui_backend.py"
if [ ! -f "$APP" ]; then
  echo "[Launcher] ERROR: $APP not found"; exit 1;
fi
echo "[Launcher] Starting GUI..."
exec "$PYTHON_BIN" "$APP"
