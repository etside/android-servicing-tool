"""
ADB Interface for Android Servicing Tool

Provides high-level interface to Android Debug Bridge (ADB) functionality:
- Device connection and management
- Shell command execution
- File transfer (push/pull)
- App installation/removal
- Device reboot options
- Screen lock management
- FRP bypass operations

Features:
- Automatic ADB binary detection
- Command timeout handling
- Error recovery
- Device state monitoring
"""

import subprocess
import time
import os
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
import platform

from .logger import Logger
from .platform_tools import PlatformToolLocator


class ADBInterface:
    """
    Android Debug Bridge interface wrapper.

    Provides Python interface to ADB commands with error handling,
    timeout management, and device state monitoring.

    Usage:
        adb = ADBInterface()
        devices = adb.get_devices()
        if devices:
            adb.shell("getprop ro.product.model")
    """

    def __init__(self, logger: Optional[Logger] = None, adb_path: Optional[str] = None):
        """
        Initialize ADB interface.

        Args:
            logger: Optional logger instance
            adb_path: Path to ADB binary (auto-detected if None)
        """
        self.logger = logger or Logger()
        self.adb_path = adb_path or self._find_adb()
        self.default_timeout = 30
        self.connected_device = None

    def _find_adb(self) -> Optional[str]:
        """Find ADB binary in bundled platform-tools or system PATH."""
        locator = PlatformToolLocator(self.logger)
        adb_path = locator.find_tool("adb")
        if adb_path:
            return adb_path

        # Fallback to common locations
        common_paths = [
            "adb",  # In PATH
            "/usr/bin/adb",
            "/usr/local/bin/adb",
            "C:\\platform-tools\\adb.exe",  # Windows Android SDK
            "C:\\adb\\adb.exe",
        ]

        for path in common_paths:
            if self._check_adb_binary(path):
                self.logger.info(f"Found ADB at: {path}")
                return path

        self.logger.warning("ADB binary not found")
        return None

    def _check_adb_binary(self, path: str) -> bool:
        """Check if ADB binary exists and works"""
        try:
            result = subprocess.run(
                [path, "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and "Android Debug Bridge" in result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def run_command(self, args: List[str], timeout: Optional[int] = None,
                   device: Optional[str] = None) -> Tuple[int, str, str]:
        """
        Run ADB command.

        Args:
            args: Command arguments (without 'adb')
            timeout: Command timeout in seconds
            device: Specific device serial

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        if not self.adb_path:
            raise RuntimeError("ADB binary not found")

        cmd = [self.adb_path]

        if device:
            cmd.extend(["-s", device])

        cmd.extend(args)

        timeout = timeout or self.default_timeout

        self.logger.debug(f"Running ADB command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return result.returncode, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            self.logger.error(f"ADB command timed out: {' '.join(cmd)}")
            return -1, "", "Command timed out"

    def get_devices(self) -> List[Dict[str, str]]:
        """
        Get list of connected ADB devices.

        Returns:
            List of device dictionaries with serial, state, etc.
        """
        returncode, stdout, stderr = self.run_command(["devices"])

        if returncode != 0:
            self.logger.error(f"Failed to get devices: {stderr}")
            return []

        devices = []
        lines = stdout.strip().split('\n')

        # Skip header
        for line in lines[1:]:
            if line.strip() and '\t' in line:
                serial, state = line.split('\t', 1)
                devices.append({
                    "serial": serial,
                    "state": state
                })

        self.logger.info(f"Found {len(devices)} ADB devices")
        return devices

    def wait_for_device(self, serial: Optional[str] = None, timeout: int = 30) -> bool:
        """
        Wait for device to be available.

        Args:
            serial: Specific device serial
            timeout: Timeout in seconds

        Returns:
            True if device available, False otherwise
        """
        args = ["wait-for-device"]
        if serial:
            args = ["-s", serial] + args

        returncode, stdout, stderr = self.run_command(args, timeout=timeout)
        return returncode == 0

    def shell(self, command: str, device: Optional[str] = None,
             timeout: Optional[int] = None) -> Tuple[bool, str]:
        """
        Execute shell command on device.

        Args:
            command: Shell command to execute
            device: Target device serial
            timeout: Command timeout

        Returns:
            Tuple of (success, output)
        """
        returncode, stdout, stderr = self.run_command(
            ["shell", command], device=device, timeout=timeout
        )

        success = returncode == 0
        output = stdout if success else stderr

        if not success:
            self.logger.error(f"Shell command failed: {command} - {output}")

        return success, output

    def push(self, local_path: str, remote_path: str,
            device: Optional[str] = None) -> bool:
        """
        Push file to device.

        Args:
            local_path: Local file path
            remote_path: Remote file path
            device: Target device serial

        Returns:
            True if successful
        """
        if not Path(local_path).exists():
            self.logger.error(f"Local file not found: {local_path}")
            return False

        returncode, stdout, stderr = self.run_command(
            ["push", local_path, remote_path], device=device
        )

        success = returncode == 0
        if not success:
            self.logger.error(f"Push failed: {stderr}")

        return success

    def pull(self, remote_path: str, local_path: str,
            device: Optional[str] = None) -> bool:
        """
        Pull file from device.

        Args:
            remote_path: Remote file path
            local_path: Local file path
            device: Target device serial

        Returns:
            True if successful
        """
        returncode, stdout, stderr = self.run_command(
            ["pull", remote_path, local_path], device=device
        )

        success = returncode == 0
        if not success:
            self.logger.error(f"Pull failed: {stderr}")

        return success

    def install(self, apk_path: str, device: Optional[str] = None,
               replace: bool = True) -> bool:
        """
        Install APK on device.

        Args:
            apk_path: Path to APK file
            device: Target device serial
            replace: Replace existing app

        Returns:
            True if successful
        """
        if not Path(apk_path).exists():
            self.logger.error(f"APK file not found: {apk_path}")
            return False

        args = ["install"]
        if replace:
            args.append("-r")
        args.append(apk_path)

        returncode, stdout, stderr = self.run_command(args, device=device)

        success = returncode == 0
        if not success:
            self.logger.error(f"Install failed: {stderr}")

        return success

    def uninstall(self, package: str, device: Optional[str] = None) -> bool:
        """
        Uninstall app from device.

        Args:
            package: Package name
            device: Target device serial

        Returns:
            True if successful
        """
        returncode, stdout, stderr = self.run_command(
            ["uninstall", package], device=device
        )

        success = returncode == 0
        if not success:
            self.logger.error(f"Uninstall failed: {stderr}")

        return success

    def reboot(self, mode: str = "system", device: Optional[str] = None) -> bool:
        """
        Reboot device.

        Args:
            mode: Reboot mode ('system', 'recovery', 'bootloader', 'fastboot')
            device: Target device serial

        Returns:
            True if successful
        """
        args = ["reboot"]
        if mode != "system":
            args.append(mode)

        returncode, stdout, stderr = self.run_command(args, device=device)

        success = returncode == 0
        if not success:
            self.logger.error(f"Reboot failed: {stderr}")

        return success

    def get_prop(self, prop: str, device: Optional[str] = None) -> Optional[str]:
        """
        Get device property.

        Args:
            prop: Property name
            device: Target device serial

        Returns:
            Property value or None
        """
        success, output = self.shell(f"getprop {prop}", device=device)
        if success:
            return output.strip()
        return None

    def set_prop(self, prop: str, value: str, device: Optional[str] = None) -> bool:
        """
        Set device property.

        Args:
            prop: Property name
            value: Property value
            device: Target device serial

        Returns:
            True if successful
        """
        return self.shell(f"setprop {prop} {value}", device=device)[0]

    def list_packages(self, device: Optional[str] = None) -> List[str]:
        """
        List installed packages.

        Args:
            device: Target device serial

        Returns:
            List of package names
        """
        success, output = self.shell("pm list packages", device=device)
        if success:
            packages = []
            for line in output.split('\n'):
                if line.startswith('package:'):
                    packages.append(line.split('package:')[1].strip())
            return packages
        return []

    def enable_usb_debugging(self, device: Optional[str] = None) -> bool:
        """
        Enable USB debugging if not already enabled.

        Args:
            device: Target device serial

        Returns:
            True if enabled or already enabled
        """
        # Check if already enabled
        debug_enabled = self.get_prop("persist.sys.usb.config", device)
        if debug_enabled and "adb" in debug_enabled:
            self.logger.info("USB debugging already enabled")
            return True

        # Try to enable via settings
        success = self.shell("settings put global adb_enabled 1", device=device)[0]
        if success:
            self.shell("settings put global development_settings_enabled 1", device=device)
            self.logger.info("USB debugging enabled")
            return True

        self.logger.warning("Failed to enable USB debugging")
        return False

    def disable_screen_lock(self, device: Optional[str] = None) -> bool:
        """
        Disable screen lock.

        Args:
            device: Target device serial

        Returns:
            True if successful
        """
        # Clear lock settings (requires root or specific permissions)
        success, output = self.shell("locksettings clear --old 0", device=device)
        if success:
            self.logger.info("Screen lock disabled")
            return True

        self.logger.warning("Failed to disable screen lock")
        return False

    def bypass_frp(self, device: Optional[str] = None) -> bool:
        """
        Attempt FRP bypass.

        Args:
            device: Target device serial

        Returns:
            True if bypass successful
        """
        # This is a simplified implementation
        # Real FRP bypass requires device-specific methods

        # Try to disable FRP via settings
        success = self.shell("settings put secure user_setup_complete 1", device=device)[0]
        if success:
            self.shell("settings put global frp_blocked 0", device=device)
            self.logger.info("FRP bypass attempted")
            return True

        self.logger.warning("FRP bypass failed")
        return False

    def get_device_info(self, device: Optional[str] = None) -> Dict[str, str]:
        """
        Get comprehensive device information.

        Args:
            device: Target device serial

        Returns:
            Dictionary of device properties
        """
        info = {}

        props = [
            "ro.product.brand",
            "ro.product.model",
            "ro.product.device",
            "ro.build.version.release",
            "ro.build.version.sdk",
            "ro.product.cpu.abi",
            "ro.hardware",
            "ro.serialno"
        ]

        for prop in props:
            value = self.get_prop(prop, device)
            if value:
                info[prop] = value

        return info