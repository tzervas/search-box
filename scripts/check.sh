#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
VENV="${CHECK_VENV:-.venv-check}"
if [[ ! -d "$VENV" ]]; then
  python3 -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install -q -U pip
[[ -f requirements.txt ]] && python -m pip install -q -r requirements.txt
[[ -f requirements-dev.txt ]] && python -m pip install -q -r requirements-dev.txt
python -m pip install -q -e . 2>/dev/null || true
if [[ -d tests ]]; then
  python -m pytest -q
fi
echo "OK: search-box checks passed"
