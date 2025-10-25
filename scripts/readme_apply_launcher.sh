#!/usr/bin/env bash
set -euo pipefail
if [ -f README.md ] && [ -f README_LAUNCHER.append.md ]; then
  printf "\n\n" >> README.md
  cat README_LAUNCHER.append.md >> README.md
  rm -f README_LAUNCHER.append.md
fi
