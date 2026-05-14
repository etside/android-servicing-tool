import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from packaging.version import InvalidVersion, Version

from .logger import Logger
from .version import __version__

DEFAULT_UPDATE_URL = 'https://statuesque-wisp-c6885a.netlify.app/version.json'


class UpdateCheckResult:
    def __init__(self, available: bool, latest_version: str, notes: str, download_url: Optional[str] = None):
        self.available = available
        self.latest_version = latest_version
        self.notes = notes
        self.download_url = download_url


class Updater:
    """Update helper for desktop unlock tool."""

    def __init__(self, logger: Optional[Logger] = None, update_url: str = DEFAULT_UPDATE_URL):
        self.logger = logger or Logger()
        self.update_url = update_url
        self.current_version = self._parse_version(__version__)

    def _parse_version(self, version_text: str) -> Optional[Version]:
        try:
            return Version(version_text)
        except InvalidVersion:
            self.logger.warning(f'Unable to parse version string: {version_text}')
            return None

    def _platform_key(self) -> str:
        if sys.platform == 'win32':
            return 'windows'
        if sys.platform == 'darwin':
            return 'macos'
        return 'linux'

    def check_for_update(self) -> Optional[UpdateCheckResult]:
        """Check the remote JSON for an updated release."""
        try:
            response = requests.get(self.update_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            latest_version = self._parse_version(data.get('version', '0.0.0'))
            if not self.current_version or not latest_version:
                return None
            if latest_version > self.current_version:
                platform_key = self._platform_key()
                download_url = str(data.get('packages', {}).get(platform_key, ''))
                notes = data.get('notes', 'A new update is available.')
                return UpdateCheckResult(True, str(latest_version), notes, download_url)
            return UpdateCheckResult(False, str(latest_version), data.get('notes', 'Up to date.'), None)
        except Exception as exc:
            self.logger.warning(f'Update check failed: {exc}')
            return None

    def download_update(self, download_url: str) -> Optional[Path]:
        """Download the update package to the user data directory."""
        if not download_url:
            return None
        try:
            app_dir = Path.home() / '.local' / 'share' / 'unlock_tool' if sys.platform != 'win32' else Path(os.getenv('APPDATA', Path.home() / 'AppData' / 'Roaming')) / 'unlock_tool'
            app_dir.mkdir(parents=True, exist_ok=True)
            filename = Path(download_url).name
            dest_path = app_dir / filename
            with requests.get(download_url, stream=True, timeout=30) as response:
                response.raise_for_status()
                with dest_path.open('wb') as handle:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            handle.write(chunk)
            return dest_path
        except Exception as exc:
            self.logger.error(f'Failed to download update: {exc}')
            return None
