#!/usr/bin/env bash
set -euo pipefail
test -x scripts/launchers/launcher.sh || { echo "launcher missing"; exit 1; }
echo "Launcher OK."
