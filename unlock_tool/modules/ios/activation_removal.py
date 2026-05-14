import os
import shutil
import subprocess
from typing import Optional


class IOSActivationRemoval:
    """iOS activation lock removal helper."""

    def __init__(self, logger=None):
        self.logger = logger

    def _run_command(self, command, timeout=120):
        try:
            if self.logger:
                self.logger.debug(f"Running activation removal command: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as exc:
            if self.logger:
                self.logger.error(f"Activation removal command failed: {exc}")
            return False, '', str(exc)

    def remove_activation_lock(self, udid: Optional[str] = None) -> bool:
        """Attempt activation lock removal using DNS or checkm8 hooks."""
        if os.path.exists('checkm8') or shutil.which('checkm8'):
            command = ['checkm8', '--activation-lock']
            if udid:
                command.extend(['-u', udid])
            success, stdout, stderr = self._run_command(command)
            if success:
                return True

        if self.logger:
            self.logger.warning('Activation lock removal requires checkm8 or manual DNS workaround.')
        return False
