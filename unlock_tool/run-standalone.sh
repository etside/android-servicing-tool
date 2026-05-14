#!/bin/bash
# Launcher script for Android Servicing Tool

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXECUTABLE="$SCRIPT_DIR/android-servicing-tool"

# Check if executable exists
if [ ! -f "$EXECUTABLE" ]; then
    echo "Error: Executable not found at $EXECUTABLE"
    echo "Please run ./build.sh first"
    exit 1
fi

# Check for root if DIAG mode might be used
if [ "$1" = "diag" ] || [ "$1" = "exploit" ] || [ "$EUID" -eq 0 ]; then
    echo "Note: Some operations require root access for USB raw device access"
    if [ "$EUID" -ne 0 ]; then
        echo "Consider running with sudo if you encounter USB permission errors"
    fi
fi

# Set library path for bundled libraries
export LD_LIBRARY_PATH="$SCRIPT_DIR:$LD_LIBRARY_PATH"
export VERCEL_API_URL="https://etool-api.vercel.app"

# Run the executable with all arguments
exec "$EXECUTABLE" "$@"