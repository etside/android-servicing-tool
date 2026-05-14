import os
import shutil
import subprocess
from typing import Optional


class iOSPasscodeBypass:
    """iOS passcode bypass helper for checkm8-capable devices."""

    def __init__(self, logger=None):
        self.logger = logger

    def _run_command(self, command, timeout=120):
        try:
            if self.logger:
                self.logger.debug(f"Running passcode bypass command: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as exc:
            if self.logger:
                self.logger.error(f"Passcode bypass command failed: {exc}")
            return False, '', str(exc)

    def bypass(self, udid: Optional[str] = None) -> bool:
        """Attempt checkm8-based passcode bypass or provide instructions."""
        if os.path.exists('checkm8') or shutil.which('checkm8'):
            command = ['checkm8']
            if udid:
                command.extend(['-u', udid])
            success, stdout, stderr = self._run_command(command)
            if success:
                return True
        if self.logger:
            self.logger.warning('checkm8 executable not found. Manual passcode bypass is required.')
        return False
