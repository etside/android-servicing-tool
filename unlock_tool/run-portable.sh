#!/usr/bin/env sh

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
  echo "Creating portable Python virtual environment..."
  python3 -m venv "$VENV_DIR"
  "$VENV_DIR/bin/python3" -m pip install --upgrade pip
  "$VENV_DIR/bin/python3" -m pip install -r "$ROOT_DIR/requirements.txt"
fi

exec "$VENV_DIR/bin/python3" "$ROOT_DIR/main.py" --gui
