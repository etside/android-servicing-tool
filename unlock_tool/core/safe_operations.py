import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from .logger import Logger


class SafeOperations:
    """Brick prevention and safe recovery helpers."""

    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()

    def backup_critical_partitions(self, device_info: Dict[str, Any]) -> bool:
        """Backup critical Android partitions before dangerous operations."""
        self.logger.info('Starting critical partition backup.')
        backup_dir = Path('backups') / device_info.get('serial', 'unknown_device')
        backup_dir.mkdir(parents=True, exist_ok=True)

        if device_info.get('platform') != 'android':
            self.logger.warning('Critical partition backup is only supported for Android devices.')
            return False

        partitions = ['boot', 'recovery', 'vbmeta', 'super']
        success = True
        for partition in partitions:
            target = backup_dir / f'{partition}.img'
            if target.exists():
                self.logger.debug(f'Backup already exists: {target}')
                continue
            self.logger.info(f'Backing up {partition} to {target}')
            if device_info.get('mode') == 'fastboot':
                self.logger.warning('Fastboot partition backup is not available in this environment; please use OEM-specific tools.')
                success = False
                continue
            try:
                if shutil.which('adb') and device_info.get('detection_method') == 'adb':
                    command = ['adb', 'shell', 'su', '-c', f'dd if=/dev/block/by-name/{partition} of=/sdcard/{partition}.img']
                    subprocess.run(command, check=True, capture_output=True, text=True, timeout=120)
                    subprocess.run(['adb', 'pull', f'/sdcard/{partition}.img', str(target)], check=True, capture_output=True, text=True, timeout=120)
                else:
                    self.logger.warning(f'Cannot backup {partition}, missing adb or unsupported device mode.')
                    success = False
            except Exception as exc:
                self.logger.error(f'Failed to backup {partition}: {exc}')
                success = False
        return success

    def validate_firmware(self, firmware_path: str, device_model: Optional[str] = None, expected_hash: Optional[str] = None) -> bool:
        """Validate firmware image files and basic compatibility."""
        firmware = Path(firmware_path)
        if not firmware.exists():
            self.logger.error(f'Firmware file does not exist: {firmware_path}')
            return False

        if expected_hash:
            self.logger.info('Validating firmware checksum.')
            digest = hashlib.sha256(firmware.read_bytes()).hexdigest()
            if digest.lower() != expected_hash.lower():
                self.logger.error('Firmware checksum validation failed.')
                return False

        if device_model and device_model.lower() not in firmware.name.lower():
            self.logger.warning('Firmware filename does not appear to match the target device model.')
        return True

    def safe_flash(self, partition: str, image: str, backup_first: bool = True, device_info: Optional[Dict[str, Any]] = None) -> bool:
        """Flash a partition safely with optional backup and rollback."""
        if backup_first and device_info:
            if not self.backup_critical_partitions(device_info):
                self.logger.warning('Backup failed, continuing with caution.')

        if not Path(image).exists():
            self.logger.error(f'Flash image not found: {image}')
            return False

        if not shutil.which('fastboot'):
            self.logger.error('fastboot binary is not available in PATH.')
            return False

        try:
            self.logger.info(f'Flashing {partition} with {image}')
            result = subprocess.run(['fastboot', 'flash', partition, image], capture_output=True, text=True, timeout=600)
            if result.returncode != 0:
                self.logger.error(f'Flash command failed: {result.stderr}')
                if backup_first and device_info:
                    backup_path = Path('backups') / device_info.get('serial', 'unknown_device') / f'{partition}.img'
                    if backup_path.exists():
                        self.logger.info('Attempting rollback using backup image.')
                        subprocess.run(['fastboot', 'flash', partition, str(backup_path)], capture_output=True, text=True, timeout=600)
                return False
            return True
        except Exception as exc:
            self.logger.error(f'Flash operation failed: {exc}')
            return False

    def ensure_ios_backup_before_restore(self, udid: Optional[str] = None) -> bool:
        """Create an iOS backup before restore operations, if possible."""
        if not shutil.which('idevicebackup2'):
            self.logger.warning('idevicebackup2 not available for iOS backup.')
            return False
        backup_dir = Path('ios_backups') / (udid or 'unknown_ios_device')
        backup_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = subprocess.run(['idevicebackup2', 'backup', str(backup_dir)], capture_output=True, text=True, timeout=600)
            if result.returncode != 0:
                self.logger.error(f'iOS backup failed: {result.stderr}')
                return False
            return True
        except Exception as exc:
            self.logger.error(f'iOS backup exception: {exc}')
            return False
