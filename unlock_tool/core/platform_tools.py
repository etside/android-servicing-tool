"""Platform tool locator for bundled ADB and Fastboot binaries."""

import os
import platform
from pathlib import Path
from typing import Optional

from .logger import Logger


class PlatformToolLocator:
    """Locate ADB/fastboot binaries from local or system paths."""

    def __init__(self, logger: Optional[Logger] = None):
        self.logger = logger or Logger()
        self.project_root = Path(__file__).resolve().parent.parent

        # Handle PyInstaller bundled exe
        import sys
        if getattr(sys, 'frozen', False):
            self.exe_dir = Path(sys.executable).resolve().parent
        else:
            self.exe_dir = self.project_root

    def _candidate_paths(self, tool_name: str) -> list[Path]:
        candidates: list[Path] = []
        extensions = ["", ".exe"] if platform.system() == "Windows" else [""]

        # Check next to the executable first (for bundled app)
        exe_platform_tools = self.exe_dir / "platform-tools"
        for ext in extensions:
            candidates.append(exe_platform_tools / f"{tool_name}{ext}")

        # Check project root
        local_dir = self.project_root / "platform-tools"
        for ext in extensions:
            candidates.append(local_dir / f"{tool_name}{ext}")
            candidates.append(local_dir / "lib64" / f"{tool_name}{ext}")

        path_env = os.environ.get("PATH", "")
        for p in path_env.split(os.pathsep):
            if p:
                candidates.append(Path(p) / tool_name)
                if platform.system() == "Windows":
                    candidates.append(Path(p) / f"{tool_name}.exe")

        # Common fallback locations
        if platform.system() == "Windows":
            candidates.extend([
                Path("C:/platform-tools") / f"{tool_name}.exe",
                Path("C:/adb") / f"{tool_name}.exe",
                Path("C:/Android/sdk/platform-tools") / f"{tool_name}.exe",
            ])
        else:
            candidates.extend([
                Path("/usr/bin") / tool_name,
                Path("/usr/local/bin") / tool_name,
                Path("/opt/android-sdk/platform-tools") / tool_name,
            ])

        return candidates

    def find_tool(self, tool_name: str) -> Optional[str]:
        """Find the executable path for the requested tool."""
        for path in self._candidate_paths(tool_name):
            if path.exists() and path.is_file() and os.access(path, os.X_OK):
                self.logger.info(f"Found {tool_name} at: {path}")
                return str(path)

        self.logger.warning(f"{tool_name} binary not found")
        return None
