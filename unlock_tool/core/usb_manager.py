"""
USB Manager for Android Servicing Tool

Handles low-level USB communication for all supported protocols:
- ADB (Android Debug Bridge)
- Fastboot
- Qualcomm Sahara/Firehose (EDL)
- MediaTek BootROM/Preloader
- Samsung Odin
- Serial COM ports

Features:
- Device enumeration and connection
- Bulk transfer operations
- Protocol detection
- Error handling and recovery
"""

import os
import re
import time
import platform
import subprocess
import threading

try:
    import usb.core
    import usb.util
    from usb.backend import libusb1
    USB_AVAILABLE = True
except ImportError:
    usb = None
    libusb1 = None
    USB_AVAILABLE = False

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    serial = None
    SERIAL_AVAILABLE = False

from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from .logger import Logger


@dataclass
class USBDevice:
    """USB device information"""
    vendor_id: int
    product_id: int
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    product: Optional[str] = None
    bus: Optional[int] = None
    address: Optional[int] = None
    interface: Optional[int] = None
    protocol: Optional[str] = None


KNOWN_MODES = {
    (0x18d1, 0xd00d): "fastboot",
    (0x18d1, 0x4ee0): "adb",
    (0x05c6, 0x9008): "qualcomm_edl",
    (0x0e8d, 0x0003): "mediatek_preloader",
    (0x0e8d, 0x2000): "mediatek_brom",
    (0x04e8, 0x6860): "samsung_adb",
    (0x04e8, 0x685d): "samsung_fastboot",
    (0x2717, 0x4ee0): "xiaomi_adb",
    (0x2717, 0x4ee2): "xiaomi_fastboot",
    (0x2717, 0x4ee4): "xiaomi_edl",
    (0x2a70, 0x4ee0): "oneplus_adb",
    (0x2a70, 0x4ee2): "oneplus_fastboot",
    (0x12d1, 0x107e): "huawei_adb",
    (0x12d1, 0x107d): "huawei_fastboot",
    (0x1004, 0x633e): "lg_fastboot",
    (0x1004, 0x633f): "lg_adb",
    (0x0bb4, 0x0c02): "htc_fastboot",
    (0x0bb4, 0x0c03): "htc_adb",
    (0x2207, 0x0010): "zte_adb",
    (0x19d2, 0x1405): "zte_fastboot",
    (0x054c, 0x05ba): "sony_fastboot",
    (0x054c, 0x0ce6): "sony_adb",
    (0x0b05, 0x18d1): "asus_fastboot",
    (0x0b05, 0x1857): "asus_adb",
    (0x1d4d, 0x0003): "samsung_download",
    (0x2a70, 0x0410): "oneplus_special",
    (0x2717, 0xff03): "xiaomi_misc",
}


class USBManager:
    """
    USB communication manager for Android devices.

    Supports multiple USB protocols and provides unified interface
    for device communication.

    Usage:
        manager = USBManager()
        devices = manager.list_devices()
        device = manager.connect_device(vendor_id=0x18d1, product_id=0x4ee7)
    """

    # Known USB IDs for Android devices
    ANDROID_USB_IDS = {
        # Google/ADB
        (0x18d1, 0x4ee7): "Google Nexus/Pixel (ADB)",
        (0x18d1, 0x4ee2): "Google Nexus/Pixel (Fastboot)",
        (0x18d1, 0x2d01): "Google Nexus/Pixel (PTP)",
        (0x18d1, 0x2d05): "Google Nexus/Pixel (MTP)",

        # Samsung
        (0x04e8, 0x6860): "Samsung Galaxy (MTP)",
        (0x04e8, 0x685d): "Samsung Galaxy (ADB)",
        (0x04e8, 0x685b): "Samsung Galaxy (Download Mode)",
        (0x04e8, 0x6601): "Samsung Galaxy (PTP)",

        # Qualcomm EDL
        (0x05c6, 0x9008): "Qualcomm (EDL Mode)",
        (0x05c6, 0x901d): "Qualcomm (Diag)",

        # MediaTek
        (0x0e8d, 0x0003): "MediaTek (Preloader)",
        (0x0e8d, 0x2000): "MediaTek (BootROM)",

        # OnePlus
        (0x2a70, 0x4ee7): "OnePlus (ADB)",
        (0x2a70, 0x4ee2): "OnePlus (Fastboot)",

        # Xiaomi
        (0x2717, 0x4ee7): "Xiaomi (ADB)",
        (0x2717, 0x4ee2): "Xiaomi (Fastboot)",

        # Huawei
        (0x12d1, 0x107e): "Huawei (ADB)",
        (0x12d1, 0x107d): "Huawei (Fastboot)",
    }

    def __init__(self, logger: Optional[Logger] = None):
        """
        Initialize USB manager.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or Logger()
        self.connected_devices: Dict[str, Any] = {}
        self._libusb_available = self._check_libusb()

    def _check_libusb(self) -> bool:
        """Check if libusb is available"""
        if not USB_AVAILABLE:
            self.logger.warning("pyusb not installed")
            return False
        try:
            usb.core.find()
            return True
        except Exception:
            self.logger.warning("libusb not available or no permissions")
            return False

    def list_devices(self) -> List[USBDevice]:
        """
        List all connected USB devices.

        Returns:
            List of USBDevice objects
        """
        devices = []

        if self._libusb_available:
            try:
                usb_devices = usb.core.find(find_all=True)
                for dev in usb_devices:
                    try:
                        device_info = USBDevice(
                            vendor_id=dev.idVendor,
                            product_id=dev.idProduct,
                            bus=dev.bus,
                            address=dev.address
                        )

                        # Try to get additional info
                        try:
                            if dev.serial_number:
                                device_info.serial_number = dev.serial_number
                        except (ValueError, usb.core.USBError) as error:
                            self.logger.debug(f"Unable to read serial_number: {error}")

                        try:
                            if dev.manufacturer:
                                device_info.manufacturer = dev.manufacturer
                        except (ValueError, usb.core.USBError) as error:
                            self.logger.debug(f"Unable to read manufacturer: {error}")

                        try:
                            if dev.product:
                                device_info.product = dev.product
                        except (ValueError, usb.core.USBError) as error:
                            self.logger.debug(f"Unable to read product: {error}")

                        # Identify protocol
                        device_info.protocol = self._identify_protocol(
                            device_info.vendor_id, device_info.product_id
                        )

                        devices.append(device_info)

                    except Exception as e:
                        self.logger.debug(f"Error reading device info: {e}")
                        continue

            except Exception as e:
                self.logger.error(f"Error listing USB devices: {e}")

        # Also check serial ports
        serial_devices = self._list_serial_devices()
        devices.extend(serial_devices)

        self.logger.info(f"Found {len(devices)} USB/serial devices")
        return devices

    def _list_serial_devices(self) -> List[USBDevice]:
        """List serial/COM devices"""
        devices = []
        try:
            ports = serial.tools.list_ports.comports()
            for port in ports:
                device = USBDevice(
                    vendor_id=0,  # Serial devices don't have VID
                    product_id=0,
                    serial_number=port.serial_number,
                    manufacturer=port.manufacturer,
                    product=port.description,
                    protocol="serial"
                )
                devices.append(device)
        except Exception as e:
            self.logger.error(f"Error listing serial devices: {e}")

        return devices

    def _identify_protocol(self, vid: int, pid: int) -> Optional[str]:
        """Identify device protocol from VID/PID"""
        key = (vid, pid)
        if key in KNOWN_MODES:
            return KNOWN_MODES[key]

        if key in self.ANDROID_USB_IDS:
            description = self.ANDROID_USB_IDS[key]
            if "ADB" in description:
                return "adb"
            elif "Fastboot" in description:
                return "fastboot"
            elif "EDL" in description:
                return "qualcomm_edl"
            elif "Preloader" in description or "BootROM" in description:
                return "mediatek_preloader"
            elif "Download Mode" in description:
                return "samsung_download"
            else:
                return "unknown"

        return None

    def connect_device(self, vendor_id: Optional[int] = None,
                      product_id: Optional[int] = None,
                      serial_number: Optional[str] = None) -> Optional[Any]:
        """
        Connect to a specific USB device.

        Args:
            vendor_id: Device vendor ID
            product_id: Device product ID
            serial_number: Device serial number

        Returns:
            Connected device handle or None
        """
        if not self._libusb_available:
            self.logger.error("libusb not available")
            return None

        try:
            dev = usb.core.find(idVendor=vendor_id, idProduct=product_id)
            if dev is None:
                self.logger.error(f"Device {vendor_id:04x}:{product_id:04x} not found")
                return None

            # Set configuration
            dev.set_configuration()

            # Claim interface
            usb.util.claim_interface(dev, 0)

            self.logger.info(f"Connected to device {vendor_id:04x}:{product_id:04x}")
            return dev

        except Exception as e:
            self.logger.error(f"Error connecting to device: {e}")
            return None

    def disconnect_device(self, device: Any):
        """Disconnect from USB device"""
        try:
            usb.util.release_interface(device, 0)
            usb.util.dispose_resources(device)
            self.logger.info("Device disconnected")
        except Exception as e:
            self.logger.error(f"Error disconnecting device: {e}")

    def bulk_transfer(self, device: Any, endpoint: int, data: bytes,
                     timeout: int = 1000) -> Optional[bytes]:
        """
        Perform bulk transfer.

        Args:
            device: USB device handle
            endpoint: Endpoint address
            data: Data to send (empty for read)
            timeout: Transfer timeout in ms

        Returns:
            Received data or None on error
        """
        try:
            if data:
                # Write
                device.write(endpoint, data, timeout=timeout)
                return None
            else:
                # Read
                return device.read(endpoint, 4096, timeout=timeout)
        except Exception as e:
            self.logger.error(f"Bulk transfer error: {e}")
            return None

    def find_android_device(self, mode: str = "adb") -> Optional[USBDevice]:
        """
        Find Android device in specific mode.

        Args:
            mode: Device mode ('adb', 'fastboot', 'edl', etc.)

        Returns:
            USBDevice if found, None otherwise
        """
        devices = self.list_devices()
        for device in devices:
            if device.protocol == mode:
                return device

        return None

    def wait_for_device(self, mode: str = "adb", timeout: int = 30) -> Optional[USBDevice]:
        """
        Wait for device to appear in specific mode.

        Args:
            mode: Expected device mode
            timeout: Timeout in seconds

        Returns:
            USBDevice if found within timeout, None otherwise
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            device = self.find_android_device(mode)
            if device:
                return device
            time.sleep(1)

        self.logger.error(f"Timeout waiting for device in {mode} mode")
        return None


class USBScanner:
    """USB device scanner and monitor for Android devices."""

    def __init__(self, logger: Optional[Logger] = None, poll_interval: float = 2.0):
        self.logger = logger or Logger()
        self.poll_interval = poll_interval
        self.backend = self._load_backend()
        self.previous_devices: Dict[str, USBDevice] = {}
        self._monitor_thread: Optional[threading.Thread] = None
        self._monitor_running = False

    def _load_backend(self):
        if not USB_AVAILABLE:
            self.logger.warning("pyusb is unavailable; USB scanning will use fallback methods")
            return None
        try:
            backend = libusb1.get_backend()
            if backend is None:
                if platform.system() == "Windows":
                    try:
                        from usb.backend import winusb
                        backend = winusb.get_backend()
                    except Exception:
                        backend = None
                if backend is None:
                    raise ValueError("No libusb backend available")
            return backend
        except Exception as exc:
            if platform.system() == "Windows":
                self.logger.warning(
                    "No libusb backend available. On Windows, install Zadig and select WinUSB/libusbK for the device."
                )
            elif platform.system() == "Darwin":
                self.logger.warning(
                    "macOS USB scanning is limited. Ensure proper libusb drivers or system extensions are installed."
                )
            else:
                self.logger.warning(f"Unable to load libusb backend: {exc}")
            return None

    def _safe_get_string(self, device: Any, index: int) -> Optional[str]:
        try:
            if index:
                return usb.util.get_string(device, index)
        except Exception as exc:
            self.logger.debug(f"Unable to read string index {index}: {exc}")
        return None

    def list_devices(self) -> List[USBDevice]:
        """Scan all connected USB devices and detect known Android modes."""
        if self.backend is None:
            self.logger.warning("pyusb backend unavailable, falling back to lsusb")
            return self._fallback_lsusb()

        devices: List[USBDevice] = []
        try:
            usb_devices = usb.core.find(find_all=True, backend=self.backend)
            for dev in usb_devices:
                try:
                    device = USBDevice(
                        vendor_id=dev.idVendor,
                        product_id=dev.idProduct,
                        serial_number=self._safe_get_string(dev, dev.iSerialNumber),
                        manufacturer=self._safe_get_string(dev, dev.iManufacturer),
                        product=self._safe_get_string(dev, dev.iProduct),
                        bus=getattr(dev, 'bus', None),
                        address=getattr(dev, 'address', None),
                        protocol=self._identify_protocol(dev.idVendor, dev.idProduct)
                    )
                    devices.append(device)
                except Exception as exc:
                    self.logger.debug(f"USB read error for {dev.idVendor:04x}:{dev.idProduct:04x}: {exc}")
                    continue
        except Exception as exc:
            if USB_AVAILABLE and (getattr(exc, 'errno', None) == 13 or 'Access' in str(exc)):
                self.logger.error("USB access denied. Missing udev rules or insufficient permissions.")
                self.logger.info(self.generate_udev_rules())
            else:
                self.logger.error(f"Unable to enumerate USB devices: {exc}")
            return self._fallback_lsusb()

        self.logger.debug(f"Scanned {len(devices)} usb devices")
        return devices

    def _fallback_lsusb(self) -> List[USBDevice]:
        if platform.system() != "Linux":
            self.logger.warning("lsusb fallback is only supported on Linux.")
            return []
        try:
            output = subprocess.check_output(["lsusb"], text=True, stderr=subprocess.DEVNULL)
        except Exception as exc:
            self.logger.error(f"lsusb fallback failed: {exc}")
            return []

        devices: List[USBDevice] = []
        for line in output.splitlines():
            parts = line.split()
            if len(parts) < 6:
                continue
            try:
                bus = int(parts[1])
                address = int(parts[3].rstrip(':'))
                vid, pid = parts[5].split(':')
                vid_int = int(vid, 16)
                pid_int = int(pid, 16)
                devices.append(USBDevice(
                    vendor_id=vid_int,
                    product_id=pid_int,
                    bus=bus,
                    address=address,
                    protocol=self._identify_protocol(vid_int, pid_int)
                ))
            except ValueError:
                continue

        return devices

    def _identify_protocol(self, vid: int, pid: int) -> Optional[str]:
        return KNOWN_MODES.get((vid, pid))

    def _device_key(self, device: USBDevice) -> str:
        return f"{device.vendor_id:04x}:{device.product_id:04x}:{device.bus}:{device.address}:{device.serial_number or ''}"

    def monitor_devices(self, callback: callable) -> None:
        """Run a background monitor that notifies callback on connect/disconnect events."""
        if self._monitor_running:
            return

        self._monitor_running = True

        def watcher():
            self.previous_devices = {self._device_key(dev): dev for dev in self.list_devices()}
            while self._monitor_running:
                current = {self._device_key(dev): dev for dev in self.list_devices()}
                added = [dev for key, dev in current.items() if key not in self.previous_devices]
                removed = [dev for key, dev in self.previous_devices.items() if key not in current]
                if added or removed:
                    self.logger.info(f"USB monitor changed: {len(added)} added, {len(removed)} removed")
                    callback(added, removed)
                    self.previous_devices = current
                time.sleep(self.poll_interval)

        self._monitor_thread = threading.Thread(target=watcher, daemon=True)
        self._monitor_thread.start()

    def stop_monitoring(self) -> None:
        self._monitor_running = False
        if self._monitor_thread is not None:
            self._monitor_thread.join(timeout=1)

    def generate_udev_rules(self) -> str:
        """Generate udev rules content for Android USB devices."""
        vendors = sorted({vid for vid, _pid in KNOWN_MODES.keys()})
        lines = ["# Android USB rules generated by unlock tool"]
        for vid in vendors:
            lines.append(f'SUBSYSTEM=="usb", ATTR{{idVendor}}=="{vid:04x}", MODE="0666", GROUP="plugdev"')
        lines.append("# Save this as /etc/udev/rules.d/51-android.rules and reload udev")
        return "\n".join(lines)


def _run_command(command: List[str], timeout: int = 15) -> Dict[str, Any]:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except FileNotFoundError:
        return {"success": False, "stdout": "", "stderr": f"Command not found: {command[0]}"}
    except subprocess.TimeoutExpired as exc:
        return {"success": False, "stdout": exc.stdout or "", "stderr": "Command timed out"}
    except Exception as exc:
        return {"success": False, "stdout": "", "stderr": str(exc)}


def _adb_devices() -> List[str]:
    result = _run_command(["adb", "devices"])
    if not result["success"]:
        return []
    devices = []
    for line in result["stdout"].splitlines():
        if line.strip() and not line.startswith("List of devices"):
            parts = line.split()
            if len(parts) >= 2 and parts[1] == "device":
                devices.append(parts[0])
    return devices


def _fastboot_devices() -> List[str]:
    result = _run_command(["fastboot", "devices"])
    if not result["success"]:
        return []
    devices = []
    for line in result["stdout"].splitlines():
        if line.strip():
            parts = line.split()
            if parts:
                devices.append(parts[0])
    return devices


def switch_to_fastboot(serial: Optional[str] = None) -> bool:
    """Switch a connected ADB device to fastboot mode."""
    if _fastboot_devices():
        return True

    command = ["adb"]
    if serial:
        command += ["-s", serial]
    command += ["reboot", "bootloader"]
    result = _run_command(command, timeout=20)
    if not result["success"]:
        return False

    for _ in range(12):
        if _fastboot_devices():
            return True
        time.sleep(2)
    return False


def switch_to_edl_qualcomm(serial: Optional[str] = None, method: str = "auto") -> bool:
    """Attempt to switch a Qualcomm device into EDL mode."""
    scanner = USBScanner()
    target_mode = "qualcomm_edl"

    def check_edl():
        time.sleep(2)
        for _ in range(10):
            devices = scanner.list_devices()
            if any(dev.protocol == target_mode for dev in devices):
                return True
            time.sleep(2)
        return False

    if method in ("adb", "auto"):
        command = ["adb"]
        if serial:
            command += ["-s", serial]
        command += ["reboot", "edl"]
        result = _run_command(command, timeout=20)
        if result["success"] and check_edl():
            return True

    if method in ("fastboot", "auto"):
        command = ["fastboot"]
        if serial:
            command += ["-s", serial]
        command += ["oem", "edl"]
        result = _run_command(command, timeout=20)
        if result["success"] and check_edl():
            return True

    return False


def enter_mediatek_brom(port: Optional[str] = None, timeout: int = 5) -> bool:
    """Try to force a MediaTek device into BROM mode using a serial break."""
    scanner = USBScanner()
    if not SERIAL_AVAILABLE:
        return False

    if port is None:
        available = [p.device for p in serial.tools.list_ports.comports()
                     if p.device and ("ACM" in p.device or "ttyACM" in p.device or "ttyUSB" in p.device)]
        port = available[0] if available else None

    if port is None:
        return False

    try:
        with serial.Serial(port, baudrate=115200, timeout=timeout) as ser:
            ser.send_break()
            time.sleep(1)
            ser.write(b"\x00\x00\x00")
            ser.flush()
    except Exception:
        return False

    for _ in range(int(timeout / 1)):
        devices = scanner.list_devices()
        if any(dev.protocol == "mediatek_brom" for dev in devices):
            return True
        time.sleep(1)

    return False


def reboot_normal(serial: Optional[str] = None) -> bool:
    """Reboot the device back to normal Android mode."""
    command = ["adb"]
    if serial:
        command += ["-s", serial]
    command += ["reboot"]
    result = _run_command(command, timeout=20)
    if result["success"]:
        return True

    command = ["fastboot"]
    if serial:
        command += ["-s", serial]
    command += ["reboot"]
    result = _run_command(command, timeout=20)
    return result["success"]


def detect_and_set_mode(target_mode: str, preferred_serial: Optional[str] = None) -> (bool, Dict[str, Any], str):
    """Detect current device mode and attempt to switch to the requested mode."""
    target_mode = target_mode.strip().lower()
    scanner = USBScanner()
    devices = scanner.list_devices()
    if not devices:
        return False, {}, "No USB devices found. Connect the device and try again."

    mode_map = {
        "fastboot": "fastboot",
        "edl": "qualcomm_edl",
        "mediatek_brom": "mediatek_brom",
        "preloader": "mediatek_preloader",
        "adb": "adb",
    }
    desired = mode_map.get(target_mode, target_mode)

    for device in devices:
        if desired == device.protocol:
            return True, device.__dict__, f"Device already in {target_mode} mode."

    adb_targets = [dev for dev in devices if dev.protocol == "adb"]
    fastboot_targets = [dev for dev in devices if dev.protocol == "fastboot"]

    serial = preferred_serial
    if serial is None:
        if adb_targets:
            serial = adb_targets[0].serial_number
        elif fastboot_targets:
            serial = fastboot_targets[0].serial_number

    if target_mode == "fastboot":
        if adb_targets:
            if switch_to_fastboot(serial=serial):
                return True, {"serial": serial, "mode": "fastboot"}, "Switched device to fastboot."
            return False, {}, "Failed to reboot device to fastboot. Verify USB debugging permissions and device state."
        if fastboot_targets:
            return True, fastboot_targets[0].__dict__, "Device already in fastboot mode."

    if target_mode == "edl":
        if adb_targets or fastboot_targets:
            if switch_to_edl_qualcomm(serial=serial, method="auto"):
                return True, {"serial": serial, "mode": "qualcomm_edl"}, "Device entered Qualcomm EDL mode."
            return False, {}, "Unable to switch to Qualcomm EDL. Try manual key combination or test-point method."

    if target_mode == "mediatek_brom":
        if enter_mediatek_brom(port=None):
            return True, {"serial": serial, "mode": "mediatek_brom"}, "MediaTek device entered BROM mode."
        return False, {}, "Unable to enter MediaTek BROM. Hold Vol Up+Vol Down while reconnecting USB."

    return False, {}, f"Target mode '{target_mode}' is not supported by automatic workflow."
