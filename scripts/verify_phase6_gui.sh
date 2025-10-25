#!/usr/bin/env bash
echo "[verify] GUI presence"
test -f app/gui/gui_app.py && echo "[ok] GUI found"
