#!/bin/bash
# Build script for Android Servicing Tool standalone Ubuntu application

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Building Android Servicing Tool for Ubuntu..."

# Check if Python 3.8+ is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "Python $PYTHON_VERSION found"
else
    echo "Error: Python 3.8+ required, found $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements-standalone.txt

# Install PyInstaller
pip install pyinstaller

# Build the application
echo "Building standalone executable..."
"$SCRIPT_DIR/.venv/bin/python" -m pyinstaller android-servicing-tool.spec --clean --noconfirm

# Check if build succeeded
if [ -f "dist/android-servicing-tool" ]; then
    echo "Build successful!"
    echo "Executable: dist/android-servicing-tool"
    echo "Size: $(stat -c%s dist/android-servicing-tool) bytes"

    # Create tar.gz
    echo "Creating distribution archive..."
    tar -czf "android-servicing-tool-linux-x86_64.tar.gz" -C dist android-servicing-tool
    echo "Archive: android-servicing-tool-linux-x86_64.tar.gz"
else
    echo "Build failed!"
    exit 1
fi

echo "Build completed successfully!"