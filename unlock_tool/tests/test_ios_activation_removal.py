import unittest
from unittest.mock import patch, MagicMock

from modules.ios.activation_removal import IOSActivationRemoval


class IOSActivationRemovalTests(unittest.TestCase):
    @patch('modules.ios.activation_removal.subprocess.run')
    @patch('modules.ios.activation_removal.shutil.which')
    def test_remove_activation_lock_success(self, mock_which, mock_run):
        mock_which.return_value = '/usr/bin/checkm8'
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = 'Success'
        mock_result.stderr = ''
        mock_run.return_value = mock_result

        remover = IOSActivationRemoval(logger=MagicMock())
        success = remover.remove_activation_lock('FAKEUDID')
        self.assertTrue(success)

    @patch('modules.ios.activation_removal.subprocess.run')
    def test_remove_activation_lock_failure(self, mock_run):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ''
        mock_result.stderr = 'Error'
        mock_run.return_value = mock_result

        remover = IOSActivationRemoval(logger=MagicMock())
        success = remover.remove_activation_lock('FAKEUDID')
        self.assertFalse(success)


if __name__ == '__main__':
    unittest.main()
