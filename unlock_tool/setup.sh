#!/bin/bash

# Setup script for portable Python

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OS="$(uname -s)"

case "$OS" in
    Linux)
        PYTHON="$SCRIPT_DIR/portable_python/linux/python/bin/python"
        ;;
    Darwin)
        PYTHON="$SCRIPT_DIR/portable_python/mac/python/bin/python"
        ;;
    *)
        echo "Unsupported OS: $OS"
        exit 1
        ;;
esac

if [ ! -x "$PYTHON" ]; then
    echo "Portable Python not found at $PYTHON"
    exit 1
fi

echo "Upgrading pip and installing requirements..."
"$PYTHON" -m pip install --upgrade pip setuptools wheel
"$PYTHON" -m pip install -r requirements.txt

echo "Setup complete. You can now run ./run.sh --gui"