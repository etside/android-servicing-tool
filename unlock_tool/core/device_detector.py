"""
Device Detector for Android and iOS devices.

This module performs automatic detection of connected devices, including Android ADB,
Fastboot, EDL, MediaTek Preloader/BROM, as well as iOS normal, recovery, and DFU modes.
"""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List

from .logger import Logger
from .usb_manager import USBScanner, USBDevice
from .adb_interface import ADBInterface
from .fastboot_interface import FastbootInterface


class DeviceDetector:
    """Detect connected Android and iOS devices."""

    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()
        self.usb_scanner = USBScanner(self.logger)
        self.adb_interface = ADBInterface(self.logger)
        self.fastboot_interface = FastbootInterface(self.logger)
        self.database = self._load_device_database()

    def _load_device_database(self) -> Dict[str, Any]:
        db_path = Path(__file__).parent.parent / 'devices.json'
        if db_path.exists():
            try:
                with db_path.open('r', encoding='utf-8') as fp:
                    return json.load(fp)
            except Exception as exc:
                self.logger.warning(f"Failed to load devices.json: {exc}")
        return {'android': {'vendors': []}, 'ios': {}}

    def detect_device(self, preferred_mode: str = 'auto') -> Optional[Dict[str, Any]]:
        preferred_mode = (preferred_mode or 'auto').strip().lower()
        self.logger.info(f"Detecting device, preferred_mode={preferred_mode}")

        # Try preferred mode first
        if preferred_mode in ['ios', 'normal', 'recovery', 'dfu']:
            ios_info = self._detect_ios(preferred_mode)
            if ios_info:
                return ios_info

        if preferred_mode in ['adb', 'fastboot', 'recovery', 'qualcomm_edl', 'mediatek_preloader', 'mediatek_brom', 'samsung_download', 'charging']:
            android_info = self._detect_android(preferred_mode)
            if android_info:
                return android_info

        # Auto-detect all modes
        ios_info = self._detect_ios()
        if ios_info:
            return ios_info

        android_info = self._detect_android()
        if android_info:
            return android_info

        self.logger.warning('No device detected')
        return None

    def _detect_android(self, preferred_mode: str = 'auto') -> Optional[Dict[str, Any]]:
        # ADB transport modes (adb, recovery, sideload, charging/offline)
        if preferred_mode in ['adb', 'recovery', 'sideload', 'charging', 'auto']:
            device = self._detect_via_adb()
            if device:
                if preferred_mode == 'auto':
                    return device
                if device.get('mode') == preferred_mode:
                    return device
                if preferred_mode in ('adb', 'recovery', 'sideload', 'charging'):
                    return device

        # Fastboot / bootloader mode
        if preferred_mode in ['fastboot', 'auto']:
            device = self._detect_via_fastboot()
            if device:
                return device

        # USB-level detection: EDL, MTK BROM/Preloader, Samsung Download, charging, MTP
        usb_modes = [
            'qualcomm_edl', 'mediatek_preloader', 'mediatek_brom',
            'samsung_download', 'charging', 'mtp', 'ptp',
            'oneplus_adb', 'oneplus_fastboot', 'oneplus_edl',
            'xiaomi_adb', 'xiaomi_fastboot', 'xiaomi_edl',
            'samsung_adb', 'samsung_fastboot',
            'huawei_adb', 'huawei_fastboot',
            'motorola_adb', 'motorola_fastboot',
            'asus_adb', 'asus_fastboot',
            'sony_adb', 'sony_fastboot',
            'lg_adb', 'lg_fastboot',
            'oppo_adb', 'realme_adb', 'vivo_adb', 'iqoo_adb',
            'itel_adb', 'tecno_adb', 'nokia_adb', 'zte_adb',
        ]
        if preferred_mode in usb_modes or preferred_mode == 'auto':
            device = self._detect_via_usb(preferred_mode)
            if device:
                return device

        return None

    def _detect_ios(self, preferred_mode: str = 'auto') -> Optional[Dict[str, Any]]:
        devices = self.usb_scanner.list_devices()
        for usb_dev in devices:
            ios_info = self._match_ios_device(usb_dev)
            if not ios_info:
                continue

            if preferred_mode == 'auto' or preferred_mode == ios_info['mode']:
                return ios_info

        return None

    def _detect_via_adb(self) -> Optional[Dict[str, Any]]:
        if not self.adb_interface.adb_path:
            return None

        devices = self.adb_interface.get_devices()
        STATE_MODE = {
            'device':      'adb',
            'recovery':    'recovery',
            'sideload':    'sideload',
            'offline':     'charging',
            'unauthorized':'unauthorized',
            'bootloader':  'fastboot',   # fastboot over ADB transport
        }
        for device in devices:
            state = device.get('state', '')
            mode = STATE_MODE.get(state)
            if not mode:
                continue
            if mode in ('charging', 'unauthorized'):
                return {
                    'serial': device['serial'],
                    'platform': 'android',
                    'detection_method': 'adb',
                    'mode': mode,
                    'model': 'Unknown' if mode == 'charging' else 'Unauthorized (allow USB debugging)',
                }
            info = self._get_device_info_adb(device['serial'])
            if info:
                info['mode'] = mode
                return info
        return None

    def _get_device_info_adb(self, serial: str) -> Optional[Dict[str, Any]]:
        info = {
            'serial': serial,
            'platform': 'android',
            'detection_method': 'adb',
            'mode': 'adb'
        }
        result = self.adb_interface.run_command(['shell', 'getprop'], device=serial, timeout=10)
        if result[0] != 0:
            # getprop failed (common in some recovery environments) — return minimal info
            return info

        stdout = result[1]
        for line in stdout.splitlines():
            if ': [' not in line or ']' not in line:
                continue
            key = line.split(': [')[0].strip()
            value = line.split(': [')[1].split(']')[0]
            if key.startswith('[') and key.endswith(']'):
                key = key[1:-1]
            if key == 'ro.product.brand':
                info['brand'] = value
                info.setdefault('manufacturer', value)
            elif key == 'ro.product.manufacturer':
                info['manufacturer'] = value
                info.setdefault('brand', value)
            elif key == 'ro.product.model':
                info['model'] = value
            elif key == 'ro.product.device':
                info['device'] = value
            elif key == 'ro.build.version.release':
                info['version'] = value
                info['android_version'] = value
            elif key == 'ro.build.type':
                if value == 'recovery':
                    info['mode'] = 'recovery'
        return info

    def _detect_via_fastboot(self) -> Optional[Dict[str, Any]]:
        if not self.fastboot_interface.fastboot_path:
            return None

        devices = self.fastboot_interface.get_devices()
        for device in devices:
            if device.get('state') == 'fastboot':
                return self._get_device_info_fastboot(device['serial'])
        return None

    def _get_device_info_fastboot(self, serial: str) -> Dict[str, Any]:
        info = {
            'serial': serial,
            'platform': 'android',
            'detection_method': 'fastboot',
            'mode': 'fastboot'
        }
        vars_to_get = [
            ('product',      'model'),
            ('serialno',     'serial_no'),
            ('version',      'bootloader_version'),
            ('secure',       'secure_boot'),
            ('unlocked',     'bootloader_unlocked'),
            ('variant',      'variant'),
            ('hw-revision',  'hw_revision'),
        ]
        for var, key in vars_to_get:
            try:
                proc = subprocess.run(
                    ['fastboot', '-s', serial, 'getvar', var],
                    capture_output=True, text=True, timeout=5
                )
                # fastboot prints getvar output to stderr
                output = proc.stderr + proc.stdout
                for line in output.splitlines():
                    if line.startswith(f'{var}:'):
                        value = line.split(':', 1)[1].strip()
                        if value:
                            info[key] = value
                        break
            except Exception:
                pass
        # Derive brand from model if possible
        if 'model' in info and 'brand' not in info:
            info['brand'] = info['model'].split()[0] if info['model'] else 'Unknown'
        return info

    def _detect_via_usb(self, preferred_mode: str = 'auto') -> Optional[Dict[str, Any]]:
        devices = self.usb_scanner.list_devices()
        for usb_dev in devices:
            match = self._match_android_device(usb_dev)
            if not match:
                continue
            if preferred_mode == 'auto' or match['mode'] == preferred_mode:
                return match
        return None

    def _match_android_device(self, usb_dev: USBDevice) -> Optional[Dict[str, Any]]:
        for vendor in self.database.get('android', {}).get('vendors', []):
            try:
                vid = int(vendor.get('vid', '0'), 16)
            except ValueError:
                continue

            if usb_dev.vendor_id != vid:
                continue

            pid_value = vendor.get('pid', 'any')
            if isinstance(pid_value, list):
                pid_match = any(usb_dev.product_id == int(pid.strip(), 16) for pid in pid_value if pid)
            else:
                pid_text = str(pid_value).strip().lower()
                if pid_text == 'any' or pid_text == '0xany':
                    pid_match = True
                else:
                    try:
                        pid_match = usb_dev.product_id == int(pid_text, 16)
                    except ValueError:
                        pid_match = False

            if not pid_match:
                continue

            return {
                'platform': 'android',
                'mode': vendor.get('mode', usb_dev.protocol or 'unknown'),
                'brand': vendor.get('brand', self._brand_from_vendor_id(usb_dev.vendor_id)),
                'serial': usb_dev.serial_number,
                'vendor_id': f'{usb_dev.vendor_id:04x}',
                'product_id': f'{usb_dev.product_id:04x}',
                'protocol': usb_dev.protocol
            }

        if usb_dev.protocol:
            return {
                'platform': 'android',
                'mode': usb_dev.protocol,
                'brand': self._brand_from_vendor_id(usb_dev.vendor_id),
                'serial': usb_dev.serial_number,
                'vendor_id': f'{usb_dev.vendor_id:04x}',
                'product_id': f'{usb_dev.product_id:04x}',
                'protocol': usb_dev.protocol
            }

        # Check KNOWN_MODES for charging/MTP PIDs not in devices.json
        from .usb_manager import KNOWN_MODES
        known_mode = KNOWN_MODES.get((usb_dev.vendor_id, usb_dev.product_id))
        if known_mode:
            return {
                'platform': 'android',
                'mode': known_mode,
                'brand': self._brand_from_vendor_id(usb_dev.vendor_id),
                'manufacturer': self._brand_from_vendor_id(usb_dev.vendor_id),
                'serial': usb_dev.serial_number,
                'vendor_id': f'{usb_dev.vendor_id:04x}',
                'product_id': f'{usb_dev.product_id:04x}',
            }

        return None

    def _brand_from_vendor_id(self, vendor_id: int) -> str:
        vendors = {
            0x18d1: 'Google',
            0x04e8: 'Samsung',
            0x2717: 'Xiaomi',
            0x2a70: 'OnePlus/Nothing',
            0x12d1: 'Huawei',
            0x22b8: 'Motorola',
            0x0b05: 'Asus',
            0x054c: 'Sony',
            0x1004: 'LG',
            0x22d9: 'Oppo/Realme/Vivo',
            0x27c6: 'Vivo',
            0x2a96: 'Itel',
            0x1572: 'Tecno',
            0x0489: 'Nokia',
            0x05c6: 'Qualcomm',
            0x0e8d: 'MediaTek'
        }
        return vendors.get(vendor_id, 'Unknown')

    def _match_ios_device(self, usb_dev: USBDevice) -> Optional[Dict[str, Any]]:
        # Fast path: protocol already resolved by KNOWN_MODES
        if usb_dev.protocol and usb_dev.protocol.startswith('ios_'):
            mode = usb_dev.protocol.replace('ios_', '')  # normal / recovery / dfu
            return {
                'platform': 'ios',
                'mode': mode,
                'brand': 'Apple',
                'serial': usb_dev.serial_number,
                'vendor_id': f'{usb_dev.vendor_id:04x}',
                'product_id': f'{usb_dev.product_id:04x}',
                'product': usb_dev.product,
                'manufacturer': usb_dev.manufacturer,
            }

        # Fallback: match against ios database
        ios_db = self.database.get('ios', {})
        if not ios_db or usb_dev.vendor_id != int(ios_db.get('vendor_id', '0'), 16):
            return None
        pid = f'{usb_dev.product_id:04x}'
        if pid in ios_db.get('normal', []):
            mode = 'normal'
        elif pid in ios_db.get('recovery', []):
            mode = 'recovery'
        elif pid in ios_db.get('dfu', []):
            mode = 'dfu'
        else:
            return None

        return {
            'platform': 'ios',
            'mode': mode,
            'brand': 'Apple',
            'serial': usb_dev.serial_number,
            'vendor_id': f'{usb_dev.vendor_id:04x}',
            'product_id': f'{usb_dev.product_id:04x}',
            'product': usb_dev.product,
            'manufacturer': usb_dev.manufacturer,
        }

    def get_device_security_info(self, device_info: Dict[str, Any]) -> Dict[str, Any]:
        if device_info.get('platform') == 'ios':
            return {
                'activation_lock': False,
                'bootrom_exploitable': True,
                'device_protected': False
            }
        return {
            'bootloader_locked': True,
            'frp_enabled': True,
            'knox_active': False,
            'tee_present': True,
            'avb_enabled': True
        }

    def get_device_database(self) -> Dict[str, Any]:
        return self.database
