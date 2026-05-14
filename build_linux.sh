#!/usr/bin/env bash
# build_linux.sh  –  Build AndroidServicingTool for Linux x86_64
# Run from:  /home/tjms/Downloads/eTool/
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV=".build_venv"
DIST="dist/AndroidServicingTool"
ARCHIVE="AndroidServicingTool-linux-x86_64.tar.gz"

echo "=== Android Servicing Tool – Linux build ==="

# ── Python check ──────────────────────────────────────────────────────────────
python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,9) else 1)" \
  || { echo "ERROR: Python 3.9+ required"; exit 1; }
echo "Python: $(python3 --version)"

# ── venv ──────────────────────────────────────────────────────────────────────
[ -d "$VENV" ] && rm -rf "$VENV"
python3 -m venv "$VENV"
source "$VENV/bin/activate"
pip install --quiet --upgrade pip wheel

# ── deps ──────────────────────────────────────────────────────────────────────
pip install --quiet \
  PyQt6==6.7.1 \
  "pyinstaller>=6.15.0" \
  pyusb==1.3.1 \
  pyserial==3.5 \
  cryptography==43.0.3 \
  pycryptodome==3.21.0 \
  requests==2.32.3 \
  psutil==6.1.0 \
  packaging==24.2

# ── build ─────────────────────────────────────────────────────────────────────
echo "Building…"
pyinstaller newui.spec --clean --noconfirm \
  --workpath build/linux --distpath dist

# ── verify ────────────────────────────────────────────────────────────────────
[ -f "$DIST/AndroidServicingTool" ] \
  || { echo "ERROR: executable not found"; exit 1; }

# ── archive ───────────────────────────────────────────────────────────────────
tar -czf "$ARCHIVE" -C dist AndroidServicingTool
echo ""
echo "✅  Build complete"
echo "    Executable : $DIST/AndroidServicingTool"
echo "    Archive    : $ARCHIVE  ($(du -sh "$ARCHIVE" | cut -f1))"
