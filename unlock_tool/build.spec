# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules, collect_all

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
    ('index.html', '.'),
]

for item, target in optional_items:
    item_path = ROOT_DIR / item
    if item_path.exists():
        datas.append((str(item_path), target))

# Add drivers if it exists
drivers_path = ROOT_DIR / 'drivers'
if drivers_path.exists():
    datas.append((str(drivers_path), 'drivers'))

project_specific = ROOT_DIR / 'platform-tools'
if project_specific.exists():
    datas.append((str(project_specific), 'platform-tools'))

if sys.platform == 'win32':
    adb = ROOT_DIR / 'platform-tools' / 'adb.exe'
    fastboot = ROOT_DIR / 'platform-tools' / 'fastboot.exe'
    if adb.exists():
        binaries.append((str(adb), '.'))
    if fastboot.exists():
        binaries.append((str(fastboot), '.'))
    libs = ROOT_DIR / 'drivers' / 'windows'
    if libs.exists():
        datas.append((str(libs), 'drivers/windows'))
elif sys.platform == 'darwin':
    for tool in ['ideviceinfo', 'idevicerestore', 'idevicebackup2', 'ideviceenterrecovery', 'irecovery', 'checkra1n']:
        path = ROOT_DIR / 'tools' / tool
        if path.exists():
            binaries.append((str(path), '.'))
    drivers_mac = ROOT_DIR / 'drivers'
    if drivers_mac.exists():
        datas.append((str(drivers_mac), 'drivers'))
else:
    for tool in ['adb', 'fastboot']:
        path = ROOT_DIR / 'platform-tools' / tool
        if path.exists():
            binaries.append((str(path), '.'))
    for tool in ['ideviceinfo', 'idevicerestore', 'idevicebackup2', 'ideviceenterrecovery', 'irecovery', 'checkra1n']:
        path = ROOT_DIR / 'tools' / tool
        if path.exists():
            binaries.append((str(path), '.'))
    drivers_linux = ROOT_DIR / 'drivers'
    if drivers_linux.exists():
        datas.append((str(drivers_linux), 'drivers'))

hidden_imports = collect_submodules('modules')

# Add web server and other critical dependencies explicitly
hidden_imports.extend([
    'http.server',
    'socketserver',
    'subprocess',
    'pathlib',
    'argparse',
    'json',
    'urllib',
    'urllib.parse',
    'webbrowser',
    'Crypto',
    'Crypto.Random',
    'Crypto.Cipher',
    'Crypto.Hash',
    'usb.core',
    'usb.util',
    'serial',
    'serial.tools.list_ports',
    'adb_shell',
    'fastboot',
])

block_cipher = None

a = Analysis(
    ['main.py', 'backend.py'],
    pathex=[str(ROOT_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe_name = 'unlock_tool.exe' if sys.platform == 'win32' else 'unlock_tool'
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Keep console for web server output
    icon=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='unlock_tool',
)
