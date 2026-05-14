import re
from typing import Dict, Optional


class FastbootFlashParser:
    """Parse fastboot flashing output for progress updates."""

    PROGRESS_REGEX = re.compile(r'(\d+)%')

    @staticmethod
    def parse_line(line: str) -> Optional[int]:
        match = FastbootFlashParser.PROGRESS_REGEX.search(line)
        if match:
            return int(match.group(1))
        return None


class IdevicerestoreParser:
    """Parse idevicerestore output for restore progress."""

    # Example: 'Restoring... 20%'
    PROGRESS_REGEX = re.compile(r'(\d+)%')

    @staticmethod
    def parse_line(line: str) -> Optional[int]:
        match = IdevicerestoreParser.PROGRESS_REGEX.search(line)
        if match:
            return int(match.group(1))
        return None


class Checkm8Parser:
    """Parse checkra1n or ipwndfu output for progress estimation."""

    PHASE_REGEX = re.compile(r'\[(\d+)/(\d+)\]')

    @staticmethod
    def parse_line(line: str) -> Optional[int]:
        match = Checkm8Parser.PHASE_REGEX.search(line)
        if match:
            current, total = int(match.group(1)), int(match.group(2))
            if total > 0:
                return int(current / total * 100)
        return None


def parse_progress_output(output: str, parser_name: str) -> Optional[int]:
    parsers: Dict[str, Any] = {
        'fastboot': FastbootFlashParser,
        'idevicerestore': IdevicerestoreParser,
        'checkm8': Checkm8Parser
    }
    parser = parsers.get(parser_name)
    if not parser:
        return None
    for line in output.splitlines():
        progress = parser.parse_line(line)
        if progress is not None:
            return progress
    return None
