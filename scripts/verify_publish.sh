#!/usr/bin/env bash
echo "[verify] Publish readiness"
test -d artifacts || mkdir -p artifacts
echo "[ok] artifacts dir ready"
