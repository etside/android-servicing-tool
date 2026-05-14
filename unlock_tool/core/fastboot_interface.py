"""
Fastboot Interface for Android Servicing Tool

Provides interface to Android Fastboot protocol for:
- Bootloader operations
- Firmware flashing
- Partition management
- OEM unlock commands
- Device reboot control

Features:
- Automatic fastboot binary detection
- Command timeout handling
- Device state verification
- Progress monitoring
"""

import subprocess
import time
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
import platform

from .logger import Logger
from .platform_tools import PlatformToolLocator


class FastbootInterface:
    """
    Android Fastboot protocol interface.

    Provides Python interface to fastboot commands for bootloader
    operations, firmware flashing, and device control.

    Usage:
        fastboot = FastbootInterface()
        devices = fastboot.get_devices()
        fastboot.flash("boot", "boot.img")
    """

    def __init__(self, logger: Optional[Logger] = None, fastboot_path: Optional[str] = None):
        """
        Initialize Fastboot interface.

        Args:
            logger: Optional logger instance
            fastboot_path: Path to fastboot binary (auto-detected if None)
        """
        self.logger = logger or Logger()
        self.fastboot_path = fastboot_path or self._find_fastboot()
        self.default_timeout = 60  # Fastboot operations can be slow

    def _find_fastboot(self) -> Optional[str]:
        """Find fastboot binary in bundled platform-tools or system PATH."""
        locator = PlatformToolLocator(self.logger)
        fastboot_path = locator.find_tool("fastboot")
        if fastboot_path:
            return fastboot_path

        common_paths = [
            "fastboot",  # In PATH
            "/usr/bin/fastboot",
            "/usr/local/bin/fastboot",
            "C:\\platform-tools\\fastboot.exe",  # Windows Android SDK
            "C:\\fastboot\\fastboot.exe",
        ]

        for path in common_paths:
            if self._check_fastboot_binary(path):
                self.logger.info(f"Found fastboot at: {path}")
                return path

        self.logger.warning("Fastboot binary not found")
        return None

    def _check_fastboot_binary(self, path: str) -> bool:
        """Check if fastboot binary exists and works"""
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and "fastboot" in result.stdout.lower()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def run_command(self, args: List[str], timeout: Optional[int] = None,
                   device: Optional[str] = None) -> Tuple[int, str, str]:
        """
        Run fastboot command.

        Args:
            args: Command arguments (without 'fastboot')
            timeout: Command timeout in seconds
            device: Specific device serial

        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        if not self.fastboot_path:
            raise RuntimeError("Fastboot binary not found")

        cmd = [self.fastboot_path]

        if device:
            cmd.extend(["-s", device])

        cmd.extend(args)

        timeout = timeout or self.default_timeout

        self.logger.debug(f"Running fastboot command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return result.returncode, result.stdout, result.stderr

        except subprocess.TimeoutExpired:
            self.logger.error(f"Fastboot command timed out: {' '.join(cmd)}")
            return -1, "", "Command timed out"

    def get_devices(self) -> List[Dict[str, str]]:
        """
        Get list of connected fastboot devices.

        Returns:
            List of device dictionaries
        """
        returncode, stdout, stderr = self.run_command(["devices"])

        if returncode != 0:
            self.logger.error(f"Failed to get devices: {stderr}")
            return []

        devices = []
        lines = stdout.strip().split('\n')

        for line in lines:
            if line.strip() and '\t' in line:
                serial, state = line.split('\t', 1)
                devices.append({
                    "serial": serial,
                    "state": state
                })

        self.logger.info(f"Found {len(devices)} fastboot devices")
        return devices

    def wait_for_device(self, serial: Optional[str] = None, timeout: int = 30) -> bool:
        """
        Wait for device to enter fastboot mode.

        Args:
            serial: Specific device serial
            timeout: Timeout in seconds

        Returns:
            True if device available, False otherwise
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            devices = self.get_devices()
            if devices:
                if serial:
                    for device in devices:
                        if device["serial"] == serial:
                            return True
                else:
                    return True
            time.sleep(1)

        self.logger.error("Timeout waiting for fastboot device")
        return False

    def reboot(self, mode: str = "system", device: Optional[str] = None) -> bool:
        """
        Reboot device from fastboot.

        Args:
            mode: Reboot mode ('system', 'recovery', 'bootloader')
            device: Target device serial

        Returns:
            True if successful
        """
        args = ["reboot"]
        if mode != "system":
            args.append(mode)

        returncode, stdout, stderr = self.run_command(args, device=device)

        success = returncode == 0
        if success:
            self.logger.info(f"Device rebooted to {mode} mode")
        else:
            self.logger.error(f"Reboot failed: {stderr}")

        return success

    def flash(self, partition: str, image_path: str,
             device: Optional[str] = None) -> bool:
        """
        Flash image to partition.

        Args:
            partition: Partition name (boot, system, recovery, etc.)
            image_path: Path to image file
            device: Target device serial

        Returns:
            True if successful
        """
        if not Path(image_path).exists():
            self.logger.error(f"Image file not found: {image_path}")
            return False

        returncode, stdout, stderr = self.run_command(
            ["flash", partition, image_path], device=device
        )

        success = returncode == 0
        if success:
            self.logger.info(f"Successfully flashed {partition}")
        else:
            self.logger.error(f"Flash failed: {stderr}")

        return success

    def erase(self, partition: str, device: Optional[str] = None) -> bool:
        """
        Erase partition.

        Args:
            partition: Partition name
            device: Target device serial

        Returns:
            True if successful
        """
        returncode, stdout, stderr = self.run_command(
            ["erase", partition], device=device
        )

        success = returncode == 0
        if success:
            self.logger.info(f"Successfully erased {partition}")
        else:
            self.logger.error(f"Erase failed: {stderr}")

        return success

    def oem_unlock(self, device: Optional[str] = None) -> bool:
        """
        Unlock OEM bootloader.

        Args:
            device: Target device serial

        Returns:
            True if successful
        """
        returncode, stdout, stderr = self.run_command(
            ["oem", "unlock"], device=device
        )

        success = returncode == 0
        if success:
            self.logger.info("OEM bootloader unlocked")
        else:
            self.logger.error(f"OEM unlock failed: {stderr}")

        return success

    def oem_lock(self, device: Optional[str] = None) -> bool:
        """
        Lock OEM bootloader.

        Args:
            device: Target device serial

        Returns:
            True if successful
        """
        returncode, stdout, stderr = self.run_command(
            ["oem", "lock"], device=device
        )

        success = returncode == 0
        if success:
            self.logger.info("OEM bootloader locked")
        else:
            self.logger.error(f"OEM lock failed: {stderr}")

        return success

    def getvar(self, variable: str, device: Optional[str] = None) -> Optional[str]:
        """
        Get fastboot variable.

        Args:
            variable: Variable name
            device: Target device serial

        Returns:
            Variable value or None
        """
        returncode, stdout, stderr = self.run_command(
            ["getvar", variable], device=device
        )

        if returncode == 0 and f"{variable}:" in stdout:
            value = stdout.split(f"{variable}:")[1].strip()
            return value

        self.logger.error(f"Failed to get variable {variable}: {stderr}")
        return None

    def set_active(self, slot: str, device: Optional[str] = None) -> bool:
        """
        Set active slot (A/B devices).

        Args:
            slot: Slot name ('a' or 'b')
            device: Target device serial

        Returns:
            True if successful
        """
        returncode, stdout, stderr = self.run_command(
            ["set_active", slot], device=device
        )

        success = returncode == 0
        if success:
            self.logger.info(f"Active slot set to {slot}")
        else:
            self.logger.error(f"Set active slot failed: {stderr}")

        return success

    def boot(self, kernel_path: str, ramdisk_path: Optional[str] = None,
            device: Optional[str] = None) -> bool:
        """
        Boot device with custom kernel.

        Args:
            kernel_path: Path to kernel image
            ramdisk_path: Optional path to ramdisk
            device: Target device serial

        Returns:
            True if successful
        """
        if not Path(kernel_path).exists():
            self.logger.error(f"Kernel file not found: {kernel_path}")
            return False

        args = ["boot", kernel_path]
        if ramdisk_path and Path(ramdisk_path).exists():
            args.extend(["--ramdisk", ramdisk_path])

        returncode, stdout, stderr = self.run_command(args, device=device)

        success = returncode == 0
        if success:
            self.logger.info("Custom kernel booted")
        else:
            self.logger.error(f"Boot failed: {stderr}")

        return success

    def continue_boot(self, device: Optional[str] = None) -> bool:
        """
        Continue normal boot process.

        Args:
            device: Target device serial

        Returns:
            True if successful
        """
        returncode, stdout, stderr = self.run_command(
            ["continue"], device=device
        )

        success = returncode == 0
        if success:
            self.logger.info("Boot continued")
        else:
            self.logger.error(f"Continue boot failed: {stderr}")

        return success

    def create_logical_partition(self, partition: str, size: str,
                               device: Optional[str] = None) -> bool:
        """
        Create logical partition (dynamic partitions).

        Args:
            partition: Partition name
            size: Size (e.g., "512M", "1G")
            device: Target device serial

        Returns:
            True if successful
        """
        returncode, stdout, stderr = self.run_command(
            ["create-logical-partition", partition, size], device=device
        )

        success = returncode == 0
        if success:
            self.logger.info(f"Logical partition {partition} created")
        else:
            self.logger.error(f"Create logical partition failed: {stderr}")

        return success

    def delete_logical_partition(self, partition: str,
                               device: Optional[str] = None) -> bool:
        """
        Delete logical partition.

        Args:
            partition: Partition name
            device: Target device serial

        Returns:
            True if successful
        """
        returncode, stdout, stderr = self.run_command(
            ["delete-logical-partition", partition], device=device
        )

        success = returncode == 0
        if success:
            self.logger.info(f"Logical partition {partition} deleted")
        else:
            self.logger.error(f"Delete logical partition failed: {stderr}")

        return success

    def resize_logical_partition(self, partition: str, size: str,
                               device: Optional[str] = None) -> bool:
        """
        Resize logical partition.

        Args:
            partition: Partition name
            size: New size
            device: Target device serial

        Returns:
            True if successful
        """
        returncode, stdout, stderr = self.run_command(
            ["resize-logical-partition", partition, size], device=device
        )

        success = returncode == 0
        if success:
            self.logger.info(f"Logical partition {partition} resized")
        else:
            self.logger.error(f"Resize logical partition failed: {stderr}")

        return success

    def get_device_info(self, device: Optional[str] = None) -> Dict[str, str]:
        """
        Get device information via fastboot.

        Args:
            device: Target device serial

        Returns:
            Dictionary of device variables
        """
        info = {}

        variables = [
            "product",
            "version",
            "serialno",
            "secure",
            "unlocked",
            "variant",
            "max-download-size"
        ]

        for var in variables:
            value = self.getvar(var, device)
            if value:
                info[var] = value

        return info