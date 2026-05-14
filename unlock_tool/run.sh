#!/bin/bash

# Portable Unlock Tool Launcher

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

# Set environment to use bundled tools
export PATH="$SCRIPT_DIR/platform-tools:$PATH"
export VERCEL_API_URL="https://etool-api.vercel.app"

# Run the tool
exec "$PYTHON" main.py "$@"