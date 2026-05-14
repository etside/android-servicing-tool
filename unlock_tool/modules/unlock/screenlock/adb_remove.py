"""
ADB screen lock removal module.

Removes screen locks using ADB commands when device is authorized.
"""

from typing import Dict, Any, Optional

from core.logger import Logger
from core.adb_interface import ADBInterface


class ADBScreenLockRemove:
    """
    ADB-based screen lock removal.

    Removes PIN, pattern, password, and biometric locks when ADB is authorized.
    Works on devices where USB debugging is enabled and device is unlocked.
    """

    def __init__(self, device_info: Dict[str, Any], logger: Optional[Logger] = None):
        self.device_info = device_info
        self.logger = logger or Logger()
        self.adb = ADBInterface(self.logger)
        self.serial = device_info.get('serial')

    def remove_lock(self) -> bool:
        """
        Remove screen lock using ADB.

        Returns:
            True if lock removed successfully, False otherwise
        """
        self.logger.info("Starting ADB screen lock removal")

        # Method 1: Clear lock settings
        if self._clear_lock_settings():
            self.logger.info("Screen lock removed via settings clear")
            return True

        # Method 2: Reset lock password
        if self._reset_lock_password():
            self.logger.info("Screen lock removed via password reset")
            return True

        # Method 3: Disable lock screen
        if self._disable_lock_screen():
            self.logger.info("Screen lock removed via lock screen disable")
            return True

        self.logger.error("All ADB screen lock removal methods failed")
        return False

    def _clear_lock_settings(self) -> bool:
        """Clear lock screen settings"""
        try:
            # Clear lock pattern
            success1 = self.adb.shell("locksettings clear --old 0000", self.serial)[0]

            # Clear password
            success2 = self.adb.shell("locksettings clear --old ''", self.serial)[0]

            # Disable lock screen
            success3 = self.adb.shell("settings put secure lockscreen.disabled 1", self.serial)[0]

            if success1 or success2 or success3:
                return True

        except Exception as e:
            self.logger.error(f"Error clearing lock settings: {e}")

        return False

    def _reset_lock_password(self) -> bool:
        """Reset lock password to empty"""
        try:
            # Try to set empty password
            success = self.adb.shell("locksettings set-password ''", self.serial)[0]
            if success:
                return True

        except Exception as e:
            self.logger.error(f"Error resetting lock password: {e}")

        return False

    def _disable_lock_screen(self) -> bool:
        """Disable lock screen entirely"""
        try:
            # Disable lock screen
            success1 = self.adb.shell("settings put secure lockscreen.disabled 1", self.serial)[0]

            # Set lock screen type to none
            success2 = self.adb.shell("settings put secure lockscreen.type 0", self.serial)[0]

            if success1 and success2:
                return True

        except Exception as e:
            self.logger.error(f"Error disabling lock screen: {e}")

        return False
