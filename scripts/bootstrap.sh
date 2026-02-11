#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${VENV_DIR:-$ROOT_DIR/.venv}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Error: Python introuvable ($PYTHON_BIN)." >&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

python -m ensurepip --upgrade
python -m pip install --upgrade pip setuptools wheel

if [ -f "$ROOT_DIR/requirements.txt" ]; then
  python -m pip install -r "$ROOT_DIR/requirements.txt"
fi

python -m pip install -e "$ROOT_DIR"
python -m pytest -q

echo "Bootstrap termine. Environnement pret dans: $VENV_DIR"
