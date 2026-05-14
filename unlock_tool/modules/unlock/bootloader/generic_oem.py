"""
Generic OEM bootloader unlock module.

Supports standard OEM unlock procedures for Android devices.
"""

from typing import Dict, Any, Optional

from core.logger import Logger
from core.adb_interface import ADBInterface
from core.fastboot_interface import FastbootInterface


class GenericOEMUnlock:
    """
    Generic OEM bootloader unlock implementation.

    Handles standard Android OEM unlock procedures including:
    - Developer options enable
    - OEM unlock toggle
    - Fastboot mode verification
    - Bootloader unlock command execution
    """

    def __init__(self, device_info: Dict[str, Any], logger: Optional[Logger] = None):
        self.device_info = device_info
        self.logger = logger or Logger()
        self.adb = ADBInterface(self.logger)
        self.fastboot = FastbootInterface(self.logger)
        self.serial = device_info.get('serial')

    def unlock(self) -> bool:
        """
        Perform OEM bootloader unlock.

        Returns:
            True if unlock successful, False otherwise
        """
        self.logger.info("Starting OEM bootloader unlock")

        # Step 1: Ensure device is in ADB mode
        if not self._ensure_adb_mode():
            self.logger.error("Failed to ensure ADB mode")
            return False

        # Step 2: Enable developer options if not already
        if not self._enable_developer_options():
            self.logger.warning("Developer options may already be enabled")

        # Step 3: Enable OEM unlock
        if not self._enable_oem_unlock():
            self.logger.error("Failed to enable OEM unlock")
            return False

        # Step 4: Reboot to fastboot
        if not self._reboot_to_fastboot():
            self.logger.error("Failed to reboot to fastboot")
            return False

        # Step 5: Perform unlock
        if not self._perform_unlock():
            self.logger.error("Failed to perform bootloader unlock")
            return False

        self.logger.info("OEM bootloader unlock completed successfully")
        return True

    def _ensure_adb_mode(self) -> bool:
        """Ensure device is in ADB mode"""
        try:
            devices = self.adb.get_devices()
            if self.serial in devices:
                return True
            self.logger.error(f"Device {self.serial} not found in ADB devices")
            return False
        except Exception as e:
            self.logger.error(f"Error checking ADB mode: {e}")
            return False

    def _enable_developer_options(self) -> bool:
        """Enable developer options"""
        try:
            # Tap build number 7 times
            for i in range(7):
                success, _ = self.adb.shell(
                    "am broadcast -a android.provider.settings.GLOBAL_SETTINGS_CHANGED",
                    self.serial
                )
                if not success:
                    self.logger.warning(f"Build number tap {i+1} failed")

            # Verify developer options enabled
            success, output = self.adb.shell("settings get global development_settings_enabled", self.serial)
            return success and output.strip() == "1"
        except Exception as e:
            self.logger.error(f"Error enabling developer options: {e}")
            return False

    def _enable_oem_unlock(self) -> bool:
        """Enable OEM unlock in developer options"""
        try:
            success = self.adb.shell("settings put global oem_unlock_enable 1", self.serial)[0]
            if success:
                self.logger.info("OEM unlock enabled")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error enabling OEM unlock: {e}")
            return False

    def _reboot_to_fastboot(self) -> bool:
        """Reboot device to fastboot mode"""
        try:
            success = self.adb.shell("reboot fastboot", self.serial)[0]
            if success:
                # Wait for device to appear in fastboot
                import time
                time.sleep(3)
                devices = self.fastboot.get_devices()
                return self.serial in devices
            return False
        except Exception as e:
            self.logger.error(f"Error rebooting to fastboot: {e}")
            return False

    def _perform_unlock(self) -> bool:
        """Execute the bootloader unlock command"""
        try:
            success, output = self.fastboot.run_command(f"oem unlock {self.serial}")
            if success:
                self.logger.info("Bootloader unlock command executed")
                return True
            self.logger.error(f"Bootloader unlock failed: {output}")
            return False
        except Exception as e:
            self.logger.error(f"Error performing unlock: {e}")
            return False
