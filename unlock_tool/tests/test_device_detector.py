import unittest
from unittest.mock import MagicMock, patch

from core.device_detector import DeviceDetector
from core.logger import Logger


class DeviceDetectorTests(unittest.TestCase):
    @patch('core.device_detector.USBScanner')
    def test_match_android_device_by_vid_pid(self, mock_scanner):
        scanner = mock_scanner.return_value
        scanner.list_devices.return_value = []
        detector = DeviceDetector(logger=Logger())
        usb_device = MagicMock()
        usb_device.vendor_id = int('18d1', 16)
        usb_device.product_id = int('4ee2', 16)
        usb_device.serial_number = 'ABC123'
        usb_device.product = 'Pixel'
        usb_device.manufacturer = 'Google'
        with patch.object(detector, '_load_device_database', return_value={'android': {'vendors': [{'vid': '0x18d1', 'pid': '0x4ee2', 'mode': 'adb', 'brand': 'Google'}]}}):
            detector.database = detector._load_device_database()
            match = detector._match_android_device(usb_device)
        self.assertIsNotNone(match)
        self.assertEqual(match['platform'], 'android')
        self.assertEqual(match['mode'], 'adb')

    @patch('core.device_detector.USBScanner')
    def test_detect_recovery_mode_android(self, mock_scanner):
        scanner = mock_scanner.return_value
        scanner.list_devices.return_value = []
        detector = DeviceDetector(logger=Logger())
        
        # Mock ADB interface to return recovery mode device
        mock_adb = MagicMock()
        mock_adb.adb_path = '/usr/bin/adb'
        mock_adb.get_devices.return_value = [{'serial': 'RECOVERY123', 'state': 'device'}]
        mock_adb.run_command.return_value = (0, '[ro.product.brand]: [Google]\n[ro.product.model]: [Pixel]\n[ro.build.type]: [recovery]\n', '')
        detector.adb_interface = mock_adb
        
        device = detector.detect_device('recovery')
        self.assertIsNotNone(device)
        self.assertEqual(device['mode'], 'recovery')
        self.assertEqual(device['platform'], 'android')

    @patch('core.device_detector.USBScanner')
    def test_match_ios_device_by_mode(self, mock_scanner):
        scanner = mock_scanner.return_value
        scanner.list_devices.return_value = []
        detector = DeviceDetector(logger=Logger())
        usb_device = MagicMock()
        usb_device.vendor_id = int('05ac', 16)
        usb_device.product_id = int('1290', 16)
        usb_device.serial_number = 'IOS123'
        usb_device.product = 'iPhone'
        usb_device.manufacturer = 'Apple'
        with patch.object(detector, '_load_device_database', return_value={'ios': {'vendor_id': '0x05ac', 'normal': ['1290'], 'recovery': [], 'dfu': []}}):
            detector.database = detector._load_device_database()
            match = detector._match_ios_device(usb_device)
        self.assertIsNotNone(match)
        self.assertEqual(match['platform'], 'ios')
        self.assertEqual(match['mode'], 'normal')

    def test_device_database_contains_2026_devices(self):
        """Test that device database includes 2026 flagship devices"""
        import json
        from pathlib import Path
        db_path = Path(__file__).parent.parent / 'database' / 'devices.json'
        with db_path.open('r', encoding='utf-8') as fp:
            db = json.load(fp)

        # Check for Android 16 support in Pixel 10
        google_devices = db.get('google', {}).get('models', {})
        pixel_10 = google_devices.get('Pixel 10')
        self.assertIsNotNone(pixel_10)
        self.assertIn('16', pixel_10.get('android_versions', []))

        # Check for iOS 19 support
        ios_devices = db.get('ios', {}).get('models', {})
        iphone_17 = ios_devices.get('iPhone17,3')  # iPhone 17 Pro
        self.assertIsNotNone(iphone_17)
        self.assertIn('19', iphone_17.get('ios_versions', []))

        # Check for Samsung S26
        samsung_devices = db.get('samsung', {}).get('models', {})
        s26 = samsung_devices.get('SM-S946B')
        self.assertIsNotNone(s26)
        self.assertIn('16', s26.get('android_versions', []))


if __name__ == '__main__':
    unittest.main()
