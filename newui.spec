# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Android Servicing Tool (newui.py)
Works on both Linux and Windows – run from the eTool/ directory.
"""
import os, sys, platform
from pathlib import Path

ROOT   = Path(os.getcwd()).resolve()          # eTool/
BACKEND = ROOT / "unlock_tool"

datas = [
    (str(BACKEND / "database"),        "unlock_tool/database"),
    (str(BACKEND / "assets"),          "unlock_tool/assets"),
    (str(BACKEND / "devices.json"),    "unlock_tool"),
    (str(BACKEND / "EULA.txt"),        "unlock_tool"),
]

# platform-tools bundled next to the exe
for pt_dir in [ROOT / "platform-tools", BACKEND / "platform-tools"]:
    if pt_dir.exists():
        datas.append((str(pt_dir), "platform-tools"))
        break

hidden_imports = [
    "PyQt6", "PyQt6.QtCore", "PyQt6.QtGui", "PyQt6.QtWidgets",
    "PyQt6.sip",
    "usb.core", "usb.util", "usb.backend.libusb1",
    "serial", "serial.tools.list_ports",
    "cryptography", "cryptography.hazmat.primitives",
    "Crypto", "Crypto.Cipher", "Crypto.Hash", "Crypto.Random",
    "requests", "json", "sqlite3",
    "core", "core.device_detector", "core.logger", "core.adb_interface",
    "core.fastboot_interface", "core.usb_manager", "core.device_profiles",
    "core.security_advisor", "core.exploit_manager", "core.platform_tools",
    "core.license_manager",
    "modules", "modules.exploits", "modules.unlock", "modules.frp",
    "modules.flash", "modules.imei", "modules.utils",
    "modules.exploits.qualcomm_diag_exploit",
    "modules.exploits.qualcomm_edl_exploit",
    "modules.exploits.mediatek_brom_exploit",
    "modules.exploits.samsung_frp_exploit",
    "modules.exploits.google_pixel_frp_exploit",
    "modules.exploits.huawei_frp_exploit",
    "modules.exploits.lockscreen_removal_exploit",
    "modules.exploits.imei_qcn_exploit",
    "modules.unlock.security.advanced_knox_bypass",
    "modules.unlock.bootloader.samsung_unlock",
    "modules.unlock.bootloader.qualcomm_secboot",
    "modules.unlock.bootloader.mediatek_brom",
    "modules.unlock.bootloader.xiaomi_unlock",
    "modules.unlock.screenlock.adb_remove",
    "modules.frp.samsung_frp", "modules.frp.google_frp",
    "modules.frp.huawei_frp", "modules.frp.xiaomi_frp",
]

IS_WIN = platform.system() == "Windows"
EXE_NAME = "AndroidServicingTool"
ICON = str(BACKEND / "assets" / "logo.svg") if (BACKEND / "assets" / "logo.svg").exists() else None

block_cipher = None

a = Analysis(
    [str(ROOT / "newui.py")],
    pathex=[str(ROOT), str(BACKEND)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "pandas", "scipy"],
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=EXE_NAME,
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon=ICON,
    uac_admin=IS_WIN,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=["vcruntime140.dll", "python3*.dll"],
    name=EXE_NAME,
)
