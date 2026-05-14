#!/usr/bin/env bash
set -e
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Running post-install checks for Unlock Tool..."

if [ "$(uname)" = "Linux" ]; then
  echo "Copying udev rules to /etc/udev/rules.d/"
  sudo cp "$ROOT_DIR/drivers/linux/50-android.rules" /etc/udev/rules.d/50-android.rules
  sudo cp "$ROOT_DIR/drivers/linux/51-edl.rules" /etc/udev/rules.d/51-edl.rules
  sudo udevadm control --reload-rules
  echo "udev rules installed. Reconnect your device and run: sudo udevadm trigger"
elif [ "$(uname)" = "Darwin" ]; then
  echo "macOS detected. Please install libimobiledevice and checkra1n if needed."
  echo "You may also need to approve system extensions in System Settings > Security & Privacy."
else
  echo "Unsupported platform for this script. Use the Windows post-install script instead."
fi
