"""
Driver Manager for unlock tool.

Provides operating-system aware driver detection, readiness checks, and
user guidance for Android and iOS connections.
"""

import platform
import shutil
import subprocess
from typing import Any, Dict, List, Optional

from .logger import Logger


class DriverManager:
    """Driver health reporter and guidance engine."""

    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()
        self.os_name = platform.system().lower()
        self.arch = platform.machine().lower()

    def get_system_summary(self) -> Dict[str, Any]:
        return {
            'os': self.os_name,
            'arch': self.arch,
            'adb_installed': self._is_installed('adb'),
            'fastboot_installed': self._is_installed('fastboot'),
            'python': shutil.which('python') or shutil.which('python3') or 'not found',
            'platform_tools': self._is_installed('adb') and self._is_installed('fastboot'),
        }

    def _is_installed(self, executable: str) -> bool:
        return shutil.which(executable) is not None

    def evaluate_device_driver_status(self, device_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        report: Dict[str, Any] = {
            'device_info': device_info or {},
            'os': self.os_name,
            'status': 'unknown',
            'available_tools': [],
            'required_drivers': [],
            'guidance': ''
        }

        report['available_tools'] = self._available_tool_list()

        if not device_info:
            report['status'] = 'no_device'
            report['guidance'] = self._generic_driver_guidance()
            return report

        platform_name = device_info.get('platform', 'unknown').lower()
        if platform_name == 'ios':
            return self._build_ios_report(device_info, report)

        return self._build_android_report(device_info, report)

    def _available_tool_list(self) -> List[str]:
        tools = []
        for tool in ['adb', 'fastboot']:
            if self._is_installed(tool):
                tools.append(tool)
        return tools

    def get_generic_driver_guidance(self) -> str:
        lines = [
            'No device was detected. Connect your phone with a USB cable and verify the cable supports data transfer.',
            'Install Android SDK Platform Tools for adb/fastboot support.',
            'On Linux, make sure udev rules are installed and your user is in the plugdev group.',
            'On Windows, install vendor USB drivers or use Zadig/WinUSB for qualcomm/edl devices.',
            'On macOS, install libimobiledevice and usbmuxd for Apple device support.',
        ]
        return '\n'.join(lines)

    def _generic_driver_guidance(self) -> str:
        return self.get_generic_driver_guidance()

    def _build_android_report(self, device_info: Dict[str, Any], report: Dict[str, Any]) -> Dict[str, Any]:
        mode = device_info.get('mode', 'unknown')
        brand = device_info.get('brand', 'Unknown')
        report['status'] = 'device_detected'
        report['required_drivers'] = self._get_android_requirements(device_info, mode, brand)
        report['guidance'] = self._format_android_guidance(device_info, report['required_drivers'])
        return report

    def _build_ios_report(self, device_info: Dict[str, Any], report: Dict[str, Any]) -> Dict[str, Any]:
        mode = device_info.get('mode', 'unknown')
        report['status'] = 'device_detected'
        report['required_drivers'] = self._get_ios_requirements(mode)
        report['guidance'] = self._format_ios_guidance(device_info, report['required_drivers'])
        return report

    def _get_android_requirements(self, device_info: Dict[str, Any], mode: str, brand: str) -> List[Dict[str, str]]:
        requirements: List[Dict[str, str]] = []
        # Base platform tooling
        if self.os_name in ('linux', 'darwin', 'windows'):
            requirements.append({
                'name': 'Android SDK Platform Tools',
                'reason': 'Required for adb and fastboot communication.'
            })

        mode = mode.lower()
        if mode in ('adb', 'samsung_adb', 'xiaomi_adb', 'oneplus_adb', 'asus_adb', 'huawei_adb', 'oppo_adb', 'vivo_adb', 'realme_adb', 'motorola_adb', 'lg_adb', 'zte_adb', 'nokia_adb'):
            requirements.append({
                'name': 'USB Debugging / ADB driver',
                'reason': 'Enable USB debugging on the phone and install the correct USB driver for the vendor.'
            })
        elif mode in ('fastboot', 'samsung_fastboot', 'xiaomi_fastboot', 'oneplus_fastboot', 'asus_fastboot', 'huawei_fastboot', 'motorola_fastboot', 'lg_fastboot', 'zte_fastboot', 'nokia_fastboot'):
            requirements.append({
                'name': 'Fastboot driver',
                'reason': 'Install fastboot-compatible USB drivers or configure libusb / udev rules.'
            })
        elif mode in ('qualcomm_edl', 'xiaomi_edl', 'oneplus_edl'):
            requirements.append({
                'name': 'Qualcomm QDLoader 9008 driver',
                'reason': 'EDL mode requires a specific Qualcomm driver on Windows or libusb support on Linux/macOS.'
            })
        elif mode in ('mediatek_preloader', 'mediatek_brom'):
            requirements.append({
                'name': 'MediaTek VCOM / BootROM driver',
                'reason': 'MediaTek devices require preloader/BROM drivers and appropriate USB permissions.'
            })
        elif mode == 'samsung_download':
            requirements.append({
                'name': 'Samsung USB / Odin driver',
                'reason': 'Download mode uses Samsung USB drivers and Odin-compatible connection settings.'
            })
        else:
            requirements.append({
                'name': 'Generic USB support',
                'reason': 'Install libusb and ensure the device is reachable through adb/fastboot or direct USB vendor drivers.'
            })

        if self.os_name == 'linux':
            rule_text = self.get_udev_rule_content([device_info.get('vendor_id')])
            requirements.append({
                'name': 'udev rules',
                'reason': 'Linux requires udev rules for non-root USB access. Save rules to /etc/udev/rules.d/51-android.rules.'
            })
        elif self.os_name == 'windows':
            requirements.append({
                'name': 'PnP driver installation',
                'reason': 'Windows devices usually require a vendor driver or Zadig to install WinUSB for Qualcomm/EDL.'
            })

        if brand.lower() == 'apple':
            requirements.append({
                'name': 'Apple Mobile Device Support',
                'reason': 'Install iTunes or Apple mobile device drivers for iOS connectivity.'
            })

        return requirements

    def _get_ios_requirements(self, mode: str) -> List[Dict[str, str]]:
        requirements = [
            {
                'name': 'libimobiledevice / usbmuxd',
                'reason': 'Required for iOS device detection, recovery, and DFU communication on non-Windows platforms.'
            }
        ]
        if self.os_name == 'windows':
            requirements.append({
                'name': 'Apple iTunes / Mobile Device Support',
                'reason': 'Install Apple drivers so Windows detects iPhone in normal, recovery, and DFU modes.'
            })
        if mode == 'dfu':
            requirements.append({
                'name': 'DFU mode readiness',
                'reason': 'Apple devices in DFU mode require a known-working Lightning cable and compatible USB controller.'
            })
        return requirements

    def _format_android_guidance(self, device_info: Dict[str, Any], requirements: List[Dict[str, str]]) -> str:
        lines = [
            f"Detected Android device: {device_info.get('brand', 'Unknown')} ({device_info.get('vendor_id', '')}:{device_info.get('product_id', '')})",
            f"Connection mode: {device_info.get('mode', 'unknown')}",
            f"Operating system: {self.os_name.title()}"
        ]
        if self.os_name == 'linux':
            lines.append('Linux note: add your user to plugdev and reload udev after creating rules.')
        if self.os_name == 'windows':
            lines.append('Windows note: install vendor drivers and use Device Manager to confirm the device is recognized.')
        if self.os_name == 'darwin':
            lines.append('macOS note: enable libusb / ioreg support with Homebrew if needed.')

        lines.append('')
        lines.append('Required driver/support items:')
        for requirement in requirements:
            lines.append(f"- {requirement['name']}: {requirement['reason']}")

        lines.append('')
        lines.append('Recommended next steps:')
        lines.append(self._recommended_action_for_mode(device_info.get('mode', 'unknown')))
        return '\n'.join(lines)

    def _recommended_action_for_mode(self, mode: str) -> str:
        if mode in ('adb', 'samsung_adb', 'xiaomi_adb', 'oneplus_adb', 'asus_adb', 'huawei_adb'):
            return 'Enable USB debugging on the device, connect with a good USB data cable, and verify `adb devices` returns the device.'
        if mode in ('fastboot', 'samsung_fastboot', 'xiaomi_fastboot', 'oneplus_fastboot', 'asus_fastboot', 'huawei_fastboot'):
            return 'Reboot the device into bootloader/fastboot and verify `fastboot devices` detects it.'
        if mode in ('qualcomm_edl', 'xiaomi_edl', 'oneplus_edl'):
            return 'Use the correct Qualcomm EDL driver on Windows or libusb support on Linux, then retry detection.'
        if mode in ('mediatek_preloader', 'mediatek_brom'):
            return 'Install MediaTek preloader/BROM drivers and use the device-specific key combination or serial break method.'
        if mode == 'samsung_download':
            return 'Install Samsung USB/Odin drivers, enter Download Mode, and confirm the device appears in Device Manager or lsusb.'
        return 'Make sure the device is connected and recognized by the system before retrying detection.'

    def _format_ios_guidance(self, device_info: Dict[str, Any], requirements: List[Dict[str, str]]) -> str:
        lines = [
            f"Detected iOS device mode: {device_info.get('mode', 'unknown')} ({device_info.get('vendor_id', '')}:{device_info.get('product_id', '')})",
            'Install the following support packages for best compatibility:'
        ]
        for requirement in requirements:
            lines.append(f"- {requirement['name']}: {requirement['reason']}")
        lines.append('')
        if device_info.get('mode') == 'dfu':
            lines.append('DFU note: use a wired connection and do not disconnect until the operation is complete.')
        return '\n'.join(lines)

    def get_udev_rule_content(self, vendor_ids: Optional[List[str]] = None) -> str:
        if vendor_ids is None or not vendor_ids:
            vendor_ids = [
                '18d1', '04e8', '2717', '2a70', '12d1', '22b8', '0b05', '054c', '1004', '22d9', '27c6', '2a96', '1572', '0489', '05c6', '0e8d'
            ]
        lines = ['# Android USB rules generated by unlock tool', 'SUBSYSTEM=="usb", MODE="0666", GROUP="plugdev"']
        for vid in vendor_ids:
            clean_vid = str(vid).lower().zfill(4)
            lines.insert(-1, f'SUBSYSTEM=="usb", ATTR{{idVendor}}=="{clean_vid}", MODE="0666", GROUP="plugdev"')
        lines.append('# Save as /etc/udev/rules.d/51-android.rules and reload udev with `sudo udevadm control --reload-rules`')
        return '\n'.join(lines)

    def get_driver_matrix(self) -> str:
        lines = [
            'Supported device families and modes:',
            '- Google Pixel: ADB, Fastboot',
            '- Motorola: ADB, Fastboot',
            '- Samsung: ADB, Fastboot, Download Mode',
            '- OnePlus / Nothing: ADB, Fastboot, EDL',
            '- Xiaomi / Redmi / POCO: ADB, Fastboot, EDL',
            '- Huawei: ADB, Fastboot',
            '- MediaTek: Preloader, BROM',
            '- Qualcomm: EDL',
            '- Sony / LG / Nokia / Asus / ZTE: ADB, Fastboot',
            '- Oppo / Realme / Vivo / iQOO: ADB, Fastboot',
            '- Tecno / Itel: ADB',
            '- Apple iOS: Normal, Recovery, DFU'
        ]
        return '\n'.join(lines)

    def _clean_vendor_id(self, vid: Optional[str]) -> str:
        if vid is None:
            return ''
        return str(vid).lower().zfill(4)

    def run_platform_command(self, command: List[str], timeout: int = 15) -> Dict[str, Any]:
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
            return {'success': result.returncode == 0, 'stdout': result.stdout.strip(), 'stderr': result.stderr.strip()}
        except FileNotFoundError:
            return {'success': False, 'stdout': '', 'stderr': f'Command not found: {command[0]}'}
        except subprocess.TimeoutExpired as exc:
            return {'success': False, 'stdout': exc.stdout or '', 'stderr': 'Command timed out'}

    def check_adb_fastboot(self) -> Dict[str, Any]:
        return {
            'adb': self.run_platform_command(['adb', 'version']),
            'fastboot': self.run_platform_command(['fastboot', 'version'])
        }
