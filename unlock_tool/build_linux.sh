#!/bin/bash
# Linux Build Script for Unlock Tool
# Run this on Linux to create the portable executable

echo "Building Unlock Tool for Linux..."
echo

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found. Please run this script from the unlock_tool directory."
    exit 1
fi

# Check if Python virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found. Please run setup.sh first."
    exit 1
fi

PYTHON_PATH="python3"  # Use venv python3

# Install PyInstaller if not present
echo "Installing PyInstaller..."
"$PYTHON_PATH" -m pip install pyinstaller --quiet

# Build the frontend first
echo "Building frontend..."
if [ -f "package.json" ]; then
    if command -v npm &> /dev/null; then
        npm run build
    else
        echo "Warning: npm not found, skipping frontend build"
    fi
fi

# Run PyInstaller
echo "Running PyInstaller..."
"$PYTHON_PATH" -m pyinstaller build.spec --clean --noconfirm

if [ $? -eq 0 ]; then
    echo
    echo "Build completed successfully!"

    # Create portable tar.gz
    echo "Creating portable tar.gz..."

    # Get current date for filename
    DATESTAMP=$(date +%Y%m%d)
    TAR_NAME="unlock_tool_linux_portable_${DATESTAMP}.tar.gz"

    if [ -d "dist/unlock_tool" ]; then
        cd dist
        tar -czf "../$TAR_NAME" unlock_tool/
        cd ..

        # Get file size
        SIZE=$(stat -c%s "$TAR_NAME" 2>/dev/null || stat -f%z "$TAR_NAME" 2>/dev/null || echo "0")
        SIZE_MB=$((SIZE / 1048576))

        echo "Portable tar.gz created: $TAR_NAME"
        echo "Size: ${SIZE_MB} MB"
        echo
        echo "SUCCESS: Linux portable build completed!"
        echo
        echo "To run: extract $TAR_NAME and execute ./unlock_tool"
    else
        echo "Error: dist/unlock_tool directory not found"
        exit 1
    fi
else
    echo
    echo "Build failed!"
    exit 1
fi