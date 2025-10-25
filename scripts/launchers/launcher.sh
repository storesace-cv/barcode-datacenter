#!/usr/bin/env bash
# Smart-Mode Launcher v3.4 — Prefer PySimpleGUI-4-foss==4.61.0.206
# Idempotent, CI-friendly, Codex/GitHub integrated

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LOG_DIR="${ROOT}/logs"
LOG_FILE="${LOG_DIR}/launcher.log"
mkdir -p "${LOG_DIR}"

# Tee everything to the launcher log while keeping console output.
exec > >(tee -a "${LOG_FILE}")
exec 2>&1

cd "$ROOT"
VENV_DIR="${ROOT}/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "[Smart-Mode] Launcher — initializing environment"
echo "[Smart-Mode] Project root: ${ROOT}"
echo "[Smart-Mode] Logging to ${LOG_FILE}"

# (1) Create / activate venv
if [ ! -d "${VENV_DIR}" ]; then
  echo "[Smart-Mode] Creating virtual environment..."
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi
# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"

# (2) Upgrade toolchain
python -m ensurepip -U >/dev/null 2>&1 || true
pip install --upgrade pip wheel setuptools >/dev/null 2>&1

# (3) Install pinned GUI lib (FOSS)
PRIMARY_SPEC="PySimpleGUI-4-foss==4.61.0.206"
FALLBACK_SPECS=("PySimpleGUI-4-foss==4.60.4.1" "PySimpleGUI==5.0.8.3")
VENDOR_WHEEL="${ROOT}/vendor/PySimpleGUI-4.60.5-py3-none-any.whl"

pip uninstall -y PySimpleGUI PySimpleGUI-4-foss || true

install_gui_pkg() {
  local spec="$1"
  local extra_args=()
  if [[ "${spec}" == PySimpleGUI-4-foss* ]]; then
    extra_args=(--index-url "https://pypi.org/simple")
  fi
  echo "[Smart-Mode] Installing ${spec}..."
  if pip install --no-cache-dir "${extra_args[@]}" "${spec}"; then
    GUI_SPEC="${spec}"
    return 0
  fi
  return 1
}

GUI_SPEC=""
if install_gui_pkg "${PRIMARY_SPEC}"; then
  GUI_SPEC="${PRIMARY_SPEC}"
else
  echo "[Smart-Mode] Primary install failed, attempting fallback options"
  if [ -f "${VENDOR_WHEEL}" ]; then
    echo "[Smart-Mode] Installing vendor wheel ${VENDOR_WHEEL}"
    if pip install "${VENDOR_WHEEL}"; then
      GUI_SPEC="PySimpleGUI==4.60.5"
    else
      echo "[Smart-Mode] ⚠️ Vendor wheel install failed"
    fi
  fi

  if [ -z "${GUI_SPEC}" ]; then
    for spec in "${FALLBACK_SPECS[@]}"; do
      if install_gui_pkg "${spec}"; then
        echo "[Smart-Mode] ✅ Fallback install succeeded"
        GUI_SPEC="${spec}"
        break
      fi
    done
  fi

  if [ -z "${GUI_SPEC}" ]; then
    echo "[Smart-Mode] ❌ Unable to install any PySimpleGUI distribution"
    exit 1
  fi
fi

EXPECTED_VERSION="${GUI_SPEC##*==}"
DIST_NAME="${GUI_SPEC%%==*}"

# (4) Verify installation (exact version + API contract)
python - "${EXPECTED_VERSION}" "${DIST_NAME}" <<'PYCODE'
import sys
from importlib import metadata
import PySimpleGUI as sg

expected, dist_name = sys.argv[1], sys.argv[2]
try:
    ver = metadata.version(dist_name)
except Exception:
    ver = str(getattr(sg, 'version', 'unknown'))
    if ver == 'unknown' and hasattr(sg, '__version__'):
        ver = str(getattr(sg, '__version__'))

print("[Smart-Mode] Detected PySimpleGUI:", ver)
assert ver.startswith(expected), f"Expected {expected}, got {ver}"
has_theme_api = hasattr(sg, "theme") or hasattr(sg, "set_options")
assert has_theme_api, "Missing theme APIs"
print("[Smart-Mode] ✅ PySimpleGUI verified")
PYCODE

# (5) Launch GUI
echo "[Smart-Mode] Launching GUI..."
python app/gui/gui_app.py || {
  echo "[Smart-Mode] ❌ GUI crashed, collecting logs"
  date -u +"[%FT%TZ] GUI launch failed" >> "${LOG_DIR}/launcher_error.log"
  exit 1
}

# (6) Update Codex + push to GitHub
if [ -f "scripts/codex/update_codex_and_push.sh" ]; then
  echo "[Smart-Mode] Updating Codex + pushing state to GitHub..."
  bash scripts/codex/update_codex_and_push.sh "deps_pysimplegui4foss_4.61.0.206"
fi

echo "[Smart-Mode] ✅ Environment ready and GUI launched (${GUI_SPEC})"
