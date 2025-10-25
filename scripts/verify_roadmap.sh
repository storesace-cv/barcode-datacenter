#!/usr/bin/env bash
set -euo pipefail
grep -q "Launcher (Smart-Mode)" docs/en/roadmap.md
echo "Roadmap verification OK."
