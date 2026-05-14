import json
import os
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

try:
    import pymobiledevice3 as pmd
    PMD_AVAILABLE = True
except ImportError:
    pmd = None
    PMD_AVAILABLE = False

from .logger import Logger
from .device_detector import DeviceDetector
from .usb_manager import USBScanner
from modules.ios.passcode_bypass import iOSPasscodeBypass
from modules.ios.activation_removal import IOSActivationRemoval


class iOSManager:
    """Manager for iOS device operations using libimobiledevice or subprocess fallbacks."""

    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()
        self.scanner = USBScanner(self.logger)
        self.detector = DeviceDetector(self.logger)

    def _run_command(self, command: List[str], timeout: int = 30) -> Dict[str, Any]:
        try:
            self.logger.debug(f"Running iOS command: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout.strip(),
                'stderr': result.stderr.strip(),
            }
        except FileNotFoundError as exc:
            return {'success': False, 'stdout': '', 'stderr': str(exc)}
        except subprocess.TimeoutExpired as exc:
            return {'success': False, 'stdout': exc.stdout or '', 'stderr': 'Command timed out'}
        except Exception as exc:
            return {'success': False, 'stdout': '', 'stderr': str(exc)}

    def list_devices(self) -> List[Dict[str, Any]]:
        """List connected iOS devices by UDID."""
        if PMD_AVAILABLE:
            try:
                return [{'udid': device.udid, 'type': 'ios'} for device in pmd.usbmux.list_devices()]
            except Exception as exc:
                self.logger.debug(f"pymobiledevice3 list failed: {exc}")

        command = ['idevice_id', '--list']
        result = self._run_command(command)
        if not result['success']:
            return []

        return [{'udid': line.strip(), 'type': 'ios'} for line in result['stdout'].splitlines() if line.strip()]

    def detect_device(self) -> Optional[Dict[str, Any]]:
        """Detect the current connected device, Android or iOS."""
        ios_devices = self.list_devices()
        if ios_devices:
            udid = ios_devices[0]['udid']
            info = self.get_device_info(udid)
            if info:
                info['platform'] = 'ios'
                return info

        android_info = self.detector.detect_device()
        if android_info:
            android_info['platform'] = 'android'
            return android_info

        return None

    def get_device_info(self, udid: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieve iOS device information from ideviceinfo or pymobiledevice3."""
        if PMD_AVAILABLE and udid:
            try:
                device = pmd.usbmux.device(udid)
                return {
                    'udid': udid,
                    'model': device.product or 'Unknown',
                    'product_type': device.product_type or 'Unknown',
                    'platform': 'ios',
                    'mode': 'normal',
                }
            except Exception as exc:
                self.logger.debug(f"pymobiledevice3 get_device_info failed: {exc}")

        command = ['ideviceinfo']
        if udid:
            command.extend(['-u', udid])
        result = self._run_command(command)
        if not result['success']:
            return None

        info = {'udid': udid, 'platform': 'ios', 'mode': 'normal'}
        for line in result['stdout'].splitlines():
            if ': ' not in line:
                continue
            key, value = line.split(': ', 1)
            if key == 'ProductType':
                info['product_type'] = value
            elif key == 'ProductVersion':
                info['version'] = value
            elif key == 'UniqueDeviceID':
                info['udid'] = value
            elif key == 'DeviceName':
                info['model'] = value
        return info

    def enter_recovery(self, udid: Optional[str] = None) -> bool:
        """Put the iOS device into recovery mode."""
        command = ['ideviceenterrecovery']
        if udid:
            command.extend(['-u', udid])
        result = self._run_command(command)
        return result['success']

    def exit_recovery(self, udid: Optional[str] = None) -> bool:
        """Exit recovery mode on the iOS device."""
        command = ['ideviceenterrecovery', '--exit']
        if udid:
            command.extend(['-u', udid])
        result = self._run_command(command)
        return result['success']

    def enter_dfu(self, udid: Optional[str] = None) -> bool:
        """Attempt to enter DFU mode using ideviceenterrecovery or irecovery."""
        if shutil.which('irecovery'):
            cmd = ['irecovery', '-c', 'dfu']
            if udid:
                cmd.extend(['-u', udid])
            result = self._run_command(cmd)
            return result['success']

        self.logger.warning('irecovery not installed; use manual DFU entry (Hold Power+Home).')
        return False

    def exit_dfu(self, udid: Optional[str] = None) -> bool:
        """Exit DFU mode on the device."""
        if shutil.which('irecovery'):
            cmd = ['irecovery', '-c', 'exit']
            if udid:
                cmd.extend(['-u', udid])
            result = self._run_command(cmd)
            return result['success']
        return False

    def backup(self, udid: Optional[str] = None, backup_path: str = 'ios_backup') -> bool:
        """Create an iOS backup using idevicebackup2."""
        os.makedirs(backup_path, exist_ok=True)
        command = ['idevicebackup2', 'backup', backup_path]
        if udid:
            command.extend(['-u', udid])
        result = self._run_command(command, timeout=300)
        return result['success']

    def restore(self, udid: Optional[str] = None, backup_path: str = 'ios_backup') -> bool:
        """Restore an iOS backup using idevicebackup2."""
        if not os.path.exists(backup_path):
            return False
        command = ['idevicebackup2', 'restore', backup_path]
        if udid:
            command.extend(['-u', udid])
        result = self._run_command(command, timeout=300)
        return result['success']

    def erase_device(self, udid: Optional[str] = None) -> bool:
        """Erase the iOS device using idevicerestore."""
        command = ['idevicerestore', '--erase']
        if udid:
            command.extend(['-u', udid])
        result = self._run_command(command, timeout=300)
        return result['success']

    def firmware_restore(self, udid: Optional[str] = None, ipsw_path: Optional[str] = None) -> bool:
        """Restore firmware to the iOS device using idevicerestore."""
        command = ['idevicerestore']
        if ipsw_path:
            command.extend(['-l', ipsw_path])
        if udid:
            command.extend(['-u', udid])
        result = self._run_command(command, timeout=600)
        return result['success']

    def passcode_bypass(self, udid: Optional[str] = None) -> bool:
        """Attempt iOS passcode bypass using checkm8 or fallback instructions."""
        bypass = iOSPasscodeBypass(self.logger)
        return bypass.bypass(udid)

    def activation_lock_removal(self, udid: Optional[str] = None) -> bool:
        """Attempt activation lock removal using DNS or checkm8."""
        removal = IOSActivationRemoval(self.logger)
        return removal.remove_activation_lock(udid)
