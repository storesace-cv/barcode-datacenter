#!/usr/bin/env bash
set -euo pipefail
grep -q "BACKUP_DIR" scripts/launchers/launcher.sh
grep -q "Library/Application Support/barcode-datacenter/backups" scripts/launchers/launcher.sh
echo "Launcher hardening verification OK."
