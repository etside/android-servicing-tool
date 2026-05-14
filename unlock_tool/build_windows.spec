# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

ROOT_DIR = Path(os.getcwd()).resolve()

binaries = []
datas = []

# Add web frontend assets
frontend_items = [
    ('dist', 'dist'),  # Built frontend
    ('src', 'src'),    # Source files for development
    ('public', 'public'),  # Public assets
    ('package.json', '.'),  # Node.js dependencies
    ('vite.config.ts', '.'),  # Vite config
    ('tsconfig.json', '.'),   # TypeScript config
    ('tailwind.config.ts', '.'),  # Tailwind config
]

for item, target in frontend_items:
    item_path = ROOT_DIR / item
    if item_path.exists():
        datas.append((str(item_path), target))

# Add optional files and directories
optional_items = [
    ('devices.json', '.'),
    ('database', 'database'),
    ('assets', 'assets'),
    ('README.md', '.'),
    ('EULA.txt', '.'),
    ('requirements.txt', '.'),
]

for item, target in optional_items:
    item_path = ROOT_DIR / item
    if item_path.exists():
        datas.append((str(item_path), target))

# Add drivers if it exists
drivers_path = ROOT_DIR / 'drivers'
if drivers_path.exists():
    datas.append((str(drivers_path), 'drivers'))

# Windows-specific binaries
if sys.platform == 'win32':
    adb = ROOT_DIR / 'platform-tools' / 'adb.exe'
    fastboot = ROOT_DIR / 'platform-tools' / 'fastboot.exe'
    if adb.exists():
        binaries.append((str(adb), '.'))
    if fastboot.exists():
        binaries.append((str(fastboot), '.'))

hidden_imports = [
    'http.server',
    'socketserver',
    'subprocess',
    'pathlib',
    'argparse',
    'json',
    'urllib',
    'webbrowser',
    'usb.core',
    'usb.util',
    'serial',
    'serial.tools.list_ports',
    'Crypto',
    'Crypto.Random',
    'Crypto.Cipher',
    'Crypto.Hash',
    'gui_main',
    'core.access_request',
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
]
    'modules.exploits.lockscreen_removal_exploit',
    'modules.exploits.imei_qcn_exploit',
]

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[str(ROOT_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='unlock_tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)