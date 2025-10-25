#!/usr/bin/env bash
set -euo pipefail
REQ="requirements.txt"
PATCH="requirements.patch.txt"
touch "$REQ"
while read -r line; do
  pkg="$(echo "$line" | sed 's/[# ].*$//')"
  [ -z "$pkg" ] && continue
  grep -qi "^${pkg%%[><=]*}" "$REQ" || echo "$line" >> "$REQ"
done < "$PATCH"
echo "Merged CI requirements into requirements.txt"
