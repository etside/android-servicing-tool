# Android Servicing Tool

A professional Android device servicing toolkit with a native PyQt6 desktop GUI (3uTools-style) and full backend integration for FRP bypass, bootloader unlock, Knox bypass, IMEI restore, and more.

---

## Features

| Category | Capabilities |
|---|---|
| **FRP Bypass** | Samsung (TalkBack / Chromium / Knox / VaultKeeper), Google Pixel, Huawei, Generic |
| **Bootloader** | Qualcomm EDL, MediaTek BROM, Samsung Odin, Xiaomi Mi Unlock |
| **Knox Bypass** | EDL bootloader patch, VaultKeeper exploit, recovery injection, security downgrade |
| **Lockscreen** | locksettings.db replace, locksettings clear (Android 10–13) |
| **IMEI / QCN** | Qualcomm DIAG NV-item read/write via serial port |
| **Security** | CVE advisory database, device risk scoring, patch recommendations |
| **Device Profiles** | 5+ built-in profiles (Samsung, Xiaomi, Pixel, OnePlus, Motorola) + JSON-extensible |

---

## Screenshots

> 3uTools-style UI — blue gradient header, dark navy nav rail, white card body

```
┌─────────────────────────────────────────────────────────────────┐
│  📱  Samsung Galaxy S24   Serial: R3CN…  Mode: adb  Android: 14 │  ← blue header
├──────┬──────────────────────────────────────────────────────────┤
│ 🏠   │  Quick Actions                                           │
│ 🔓   │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│ 🛡️  │  │ FRP      │ │ ⚡ Full  │ │ Knox     │ │ DIAG     │   │
│ 📋   │  │ Bypass   │ │ Chain    │ │ Bypass   │ │ Exploit  │   │
│ ⚙️   │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│ 📟   │                                                          │
└──────┴──────────────────────────────────────────────────────────┘
```

---

## Requirements

### Desktop (Linux / Windows)
- Python 3.9+
- PyQt6
- ADB / Fastboot in PATH (or bundled `platform-tools/`)
- For USB exploits: `pyusb`, `libusb`

### Android Admin APK
- Android 8.0+ device
- Used for license token generation and approval

---

## Installation

### Linux

```bash
git clone https://github.com/etside/android-servicing-tool.git
cd android-servicing-tool

# Install Python deps
pip install PyQt6 pyusb pyserial cryptography pycryptodome requests psutil

# Run directly
python3 newui.py
```

### Windows

```bat
git clone https://github.com/etside/android-servicing-tool.git
cd android-servicing-tool

pip install PyQt6 pyusb pyserial cryptography pycryptodome requests psutil
python newui.py
```

---

## Build Standalone Executables

### Linux → `.tar.gz`

```bash
bash build_linux.sh
# Output: AndroidServicingTool-linux-x86_64.tar.gz
# Run:    dist/AndroidServicingTool/AndroidServicingTool
```

### Windows → `.zip`

```bat
build_windows.bat
REM Output: AndroidServicingTool-windows-x64.zip
REM Run:    dist\AndroidServicingTool\AndroidServicingTool.exe
```

Both scripts create an isolated venv, install pinned deps, and produce a self-contained folder via PyInstaller.

---

## Android Admin APK

Located in `unlock_tool/android_admin_apk/`.

### Build

```bash
cd unlock_tool/android_admin_apk
./gradlew assembleRelease
# APK: build/outputs/apk/release/app-release-signed.apk
```

### Usage

1. Open the APK on an Android device
2. **Generate** — enter customer name, expiry date, features → tap **Generate License Token**
3. **Copy** — tap Copy to clipboard
4. **Verify & Approve** — paste any token → tap **Verify & Approve** to validate the RSA-SHA256 signature

Available feature flags: `frp_bypass`, `knox_bypass`, `diag`, `mtk_brom`, `lockscreen`, `imei`, `full_chain`

---

## Project Structure

```
eTool/
├── newui.py                    # Main PyQt6 GUI (3uTools-style)
├── newui.spec                  # PyInstaller spec (Linux + Windows)
├── build_linux.sh              # Linux build script
├── build_windows.bat           # Windows build script
└── unlock_tool/
    ├── core/
    │   ├── exploit_manager.py  # Orchestrates all exploits
    │   ├── device_detector.py  # ADB / Fastboot / USB detection
    │   ├── device_profiles.py  # Device compatibility database
    │   ├── security_advisor.py # CVE tracking & risk scoring
    │   ├── adb_interface.py    # ADB wrapper
    │   └── license_manager.py  # License validation
    ├── modules/
    │   ├── exploits/           # Qualcomm EDL/DIAG, MTK BROM, FRP, lockscreen, IMEI
    │   ├── unlock/             # Knox bypass, bootloader unlock
    │   ├── frp/                # Brand-specific FRP modules
    │   └── flash/              # Odin, fastboot, EDL flash
    ├── database/
    │   ├── device_profiles.json
    │   └── security_cves.json
    └── android_admin_apk/      # License admin Android app
```

---

## Backend Integration

The GUI imports directly from `unlock_tool/core/` and `unlock_tool/modules/`. If the backend is not found, the UI runs in demo mode.

```python
from core.exploit_manager  import ExploitManager
from core.device_profiles  import DeviceProfileManager
from core.security_advisor import SecurityAdvisor
from core.device_detector  import DeviceDetector
```

Each exploit button runs its corresponding class in a `QThread` to keep the UI responsive.

---

## License

See `unlock_tool/EULA.txt`. License tokens are generated via the Android Admin APK and validated at runtime by `core/license_manager.py`.
