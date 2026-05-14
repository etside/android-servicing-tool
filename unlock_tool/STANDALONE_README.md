# Android Servicing Tool - Standalone Ubuntu Application

A native desktop application for Android device unlocking and servicing operations.

## Features

- **Native GUI**: Qt-based desktop interface (no web browser required)
- **Device Detection**: Automatic detection of connected Android devices
- **Exploit Operations**: Qualcomm DIAG, Knox bypass, full unlock chains
- **Security Analysis**: Device security scoring and CVE tracking
- **CLI Compatibility**: All original command-line features preserved

## System Requirements

- Ubuntu 20.04 or later (x86_64)
- 4GB RAM minimum
- USB ports for device connection
- Root access for some operations (DIAG mode)

### Required System Packages

```bash
sudo apt update
sudo apt install libusb-1.0-0 libqt6widgets6 libqt6gui6 libqt6core6 python3 python3-pip
```

## Installation

1. **Download** the `android-servicing-tool-linux-x86_64.tar.gz` archive
2. **Extract** to your desired location:
   ```bash
   tar -xzf android-servicing-tool-linux-x86_64.tar.gz
   cd android-servicing-tool
   ```
3. **Make executable** (if needed):
   ```bash
   chmod +x android-servicing-tool
   ```

## Udev Rules Setup

For USB device access, install the udev rules:

```bash
sudo cp 50-android.rules /etc/udev/rules.d/
sudo cp 51-edl.rules /etc/udev/rules.d/
sudo cp 69-libmtp.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## Usage

### GUI Mode (Recommended)

```bash
./run-standalone.sh gui
```

Or double-click the executable if associated.

### Command Line Mode

```bash
./run-standalone.sh detect          # Detect devices
./run-standalone.sh list            # List all devices
./run-standalone.sh info <serial>   # Device information
./run-standalone.sh gui             # Launch GUI
```

## GUI Walkthrough

1. **Device Detection**: Click "Refresh Devices" to scan for connected devices
2. **Device Selection**: Choose your device from the dropdown
3. **Device Info**: View brand, model, chipset, Android version, and security score
4. **Operations**:
   - **Qualcomm DIAG Exploit**: Run DIAG mode exploit
   - **Knox Bypass**: Bypass Samsung Knox security
   - **Full Unlock Chain**: Complete device unlock sequence
5. **Progress & Logs**: Monitor operation progress and detailed logs

## Desktop Integration

To add to desktop menu:

```bash
cp android-servicing-tool.desktop ~/.local/share/applications/
# Edit the Exec and Icon paths in the .desktop file to match your installation
```

## Troubleshooting

### USB Permission Errors

If you see USB permission denied errors:

```bash
sudo ./run-standalone.sh gui
```

Or add your user to the `plugdev` group:

```bash
sudo usermod -a -G plugdev $USER
# Log out and back in
```

### Missing Libraries

If the application fails to start, check for missing libraries:

```bash
ldd android-servicing-tool
```

Install any missing dependencies with `sudo apt install <package>`.

### GUI Doesn't Start

Ensure you have a display server (X11/Wayland) and Qt libraries:

```bash
sudo apt install libqt6widgets6 libqt6gui6 libqt6core6
```

## Building from Source

If you have the source code:

```bash
./build.sh
```

This creates the standalone executable and tar.gz archive.

## Uninstall

Simply delete the extracted directory:

```bash
rm -rf android-servicing-tool/
```

Remove desktop entry if added:

```bash
rm ~/.local/share/applications/android-servicing-tool.desktop
```

## Security Note

This tool performs advanced device operations that may void warranties or brick devices. Use at your own risk and ensure you have backups of important data.

## License

See LICENSE.md for licensing information.