#!/usr/bin/env python3
"""
Integration test for Waydroid support and portable Python functionality.
This test verifies that the tool can detect and interact with Waydroid containers.
"""

import unittest
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, Any

from core.safe_operations import SafeOperations
from core.logger import Logger
from core.platform_tools import PlatformToolLocator
from core.driver_manager import DriverManager
from core.device_detector import DeviceDetector


class WaydroidIntegrationTests(unittest.TestCase):
    """Test tool functionality with Waydroid Android container"""

    @staticmethod
    def _is_waydroid_available() -> bool:
        """Check if waydroid is installed and accessible"""
        try:
            result = subprocess.run(['which', 'waydroid'], capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    @classmethod
    def setUpClass(cls):
        cls.logger = Logger()

    def test_waydroid_availability(self):
        """Test waydroid command availability"""
        # Skip if waydroid not available
        if not self._is_waydroid_available():
            self.skipTest("Waydroid not installed")

    def test_portable_python_available(self):
        """Test that portable Python is available"""
        project_root = Path(__file__).resolve().parent.parent
        linux_python = project_root / "portable_python/linux/python/bin/python"
        windows_python = project_root / "portable_python/windows/python/python.exe"
        mac_python = project_root / "portable_python/mac/python/bin/python"
        
        if not (linux_python.exists() or windows_python.exists() or mac_python.exists()):
            self.skipTest("Portable Python not available in this environment")
        
        self.assertTrue(True)  # If we reach here, portable Python exists

    def test_firmware_validation(self):
        """Test firmware file validation"""
        safe_ops = SafeOperations(self.logger)

        # Test with non-existent file
        self.assertFalse(safe_ops.validate_firmware("/nonexistent/file.zip"))

        # Test with existing file (create a dummy file)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
            temp_file.write(b'dummy firmware content')
            temp_path = temp_file.name

        try:
            # Should pass basic validation
            self.assertTrue(safe_ops.validate_firmware(temp_path, "TestDevice"))
        finally:
            Path(temp_path).unlink()

    def test_firmware_validation_with_hash(self):
        """Test firmware validation with expected hash"""
        safe_ops = SafeOperations(self.logger)

        import tempfile
        import hashlib

        # Create a test file with known content
        test_content = b'test firmware data'
        expected_hash = hashlib.sha256(test_content).hexdigest()

        with tempfile.NamedTemporaryFile(suffix='.img', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_path = temp_file.name

        try:
            # Should pass with correct hash
            self.assertTrue(safe_ops.validate_firmware(temp_path, "TestDevice", expected_hash))

            # Should fail with wrong hash
            self.assertFalse(safe_ops.validate_firmware(temp_path, "TestDevice", "wronghash"))
        finally:
            Path(temp_path).unlink()

    def test_platform_tools_available(self):
        """Test that bundled platform tools are available"""
        locator = PlatformToolLocator(logger=self.logger)
        adb = locator.find_tool('adb')
        fastboot = locator.find_tool('fastboot')
        
        self.assertIsNotNone(adb, "ADB tool not found")
        self.assertIsNotNone(fastboot, "Fastboot tool not found")

    def test_driver_manager_initialization(self):
        """Test driver manager initialization"""
        manager = DriverManager(logger=self.logger)
        summary = manager.get_system_summary()
        
        self.assertIn('os', summary)
        self.assertIn('arch', summary)
        self.assertIn('adb_installed', summary)
        self.assertIn('fastboot_installed', summary)

    def test_device_detector_initialization(self):
        """Test device detector initialization"""
        detector = DeviceDetector(logger=self.logger)
        
        # Should not raise exceptions on initialization
        self.assertIsNotNone(detector)
        self.assertIsNotNone(detector.usb_scanner)

    def test_waydroid_status_check(self):
        """Test waydroid command availability"""
        # Skip if waydroid not available
        if not self._is_waydroid_available():
            self.skipTest("Waydroid not installed")
        
        result = subprocess.run(
            ['waydroid', 'status'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Should return some output about session status
        self.assertIn('Session:', result.stdout)

    def test_driver_guidance_generation(self):
        """Test that driver guidance can be generated"""
        manager = DriverManager(logger=self.logger)
        guidance = manager.get_generic_driver_guidance()
        
        self.assertTrue(len(guidance) > 0)
        self.assertIn('USB', guidance)

    def test_udev_rules_generation(self):
        """Test udev rules generation for Linux"""
        manager = DriverManager(logger=self.logger)
        rules_content = manager.get_udev_rule_content()
        
        self.assertIn('SUBSYSTEM=="usb"', rules_content)
        self.assertIn('plugdev', rules_content)

    def test_driver_matrix_available(self):
        """Test that driver compatibility matrix is available"""
        manager = DriverManager(logger=self.logger)
        matrix = manager.get_driver_matrix()
        
        self.assertIn('Pixel', matrix)
        self.assertIn('Qualcomm', matrix)
        self.assertIn('MediaTek', matrix)


class PortablePythonTests(unittest.TestCase):
    """Test portable Python functionality"""

    def test_requirements_installed(self):
        """Verify key requirements are installed"""
        try:
            import PyQt6
            import usb  # pyusb package
            import serial
            import cryptography
            self.assertTrue(True, "All key requirements installed")
        except ImportError as e:
            self.fail(f"Missing required package: {e}")

    def test_core_modules_importable(self):
        """Test that core modules can be imported"""
        try:
            from core import device_detector
            from core import driver_manager
            from core import platform_tools
            from core import usb_manager
            from core import logger
            self.assertTrue(True, "All core modules importable")
        except ImportError as e:
            self.fail(f"Failed to import core module: {e}")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
