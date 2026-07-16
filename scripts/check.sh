#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

# Optional secrets scan (local hygiene; skip if git-secrets not installed)
if command -v git-secrets >/dev/null 2>&1; then
  git secrets --scan
else
  echo "note: git-secrets not installed; skip secrets scan"
fi

# Version files should agree
if [[ -f VERSION && -f pyproject.toml ]]; then
  ver_file=$(tr -d '[:space:]' < VERSION)
  ver_py=$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
  if [[ "$ver_file" != "$ver_py" ]]; then
    echo "ERROR: VERSION ($ver_file) != pyproject.toml ($ver_py)" >&2
    exit 1
  fi
fi

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
