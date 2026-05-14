import base64
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from core.license_manager import check_license_file, verify_license, _is_revoked

VALID_LICENSE_TEMPLATE = {
    'payload': {
        'user': 'Test User',
        'expiry': None,
        'features': ['android_frp', 'ios_passcode', 'ios_flashing'],
        'license_id': 'TEST-0001'
    },
    'signature': ''
}


class LicenseManagerTests(unittest.TestCase):
    def test_verify_license_invalid_base64(self):
        result = verify_license('not-base64')
        self.assertFalse(result['valid'])
        self.assertIn('valid Base64', result['error'])

    def test_verify_license_missing_payload(self):
        payload = {'signature': 'dGVzdA=='}
        token = base64.b64encode(json.dumps(payload).encode('utf-8')).decode('utf-8')
        result = verify_license(token)
        self.assertFalse(result['valid'])
        self.assertIn('missing payload', result['error'])

    @mock.patch('core.license_manager._load_public_key')
    def test_verify_license_invalid_signature(self, mock_key):
        mock_key.return_value = mock.Mock()
        result = verify_license(base64.b64encode(json.dumps({'payload': {}, 'signature': 'AAA='}).encode('utf-8')).decode('utf-8'))
        self.assertFalse(result['valid'])

    @mock.patch('core.license_manager.requests.get')
    def test_blacklist_network_fallback(self, mock_get):
        from core.license_manager import BLACKLIST_URL
        mock_get.side_effect = Exception('offline')
        self.assertFalse(_is_revoked('unknown-license'))

    def test_check_license_file_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch('core.license_manager.LICENSE_FILE', Path(temp_dir) / 'license.bin'):
                self.assertFalse(check_license_file())


if __name__ == '__main__':
    unittest.main()
