"""Device modes and preparation guidance module."""

import json
from pathlib import Path
from typing import Dict, List, Optional


class DeviceModeGuide:
    """Provides device mode information and setup guidance."""

    def __init__(self):
        """Initialize the mode guide by loading modes.json database."""
        db_path = Path(__file__).parent.parent / "database" / "modes.json"
        try:
            with open(db_path, 'r') as f:
                self.modes = json.load(f)
        except FileNotFoundError:
            self.modes = {}

    def get_mode_info(self, mode: str) -> Dict:
        """Get information for a specific device mode."""
        return self.modes.get(mode, {})

    def get_all_modes(self) -> List[str]:
        """Get list of all available modes."""
        return list(self.modes.keys())

    def get_setup_steps(self, mode: str) -> List[str]:
        """Get setup steps for a specific mode."""
        mode_info = self.modes.get(mode, {})
        return mode_info.get("setup_steps", [])

    def get_troubleshooting(self, mode: str) -> List[str]:
        """Get troubleshooting tips for a specific mode."""
        mode_info = self.modes.get(mode, {})
        return mode_info.get("troubleshooting", [])

    def modes_for_action(self, action: str) -> List[str]:
        """Get device modes required for a specific action."""
        required_modes = []
        for mode, info in self.modes.items():
            if action in info.get("required_for", []):
                required_modes.append(mode)
        return required_modes

    def format_mode_guide(self, mode: str) -> str:
        """Format complete mode guide as readable text."""
        mode_info = self.modes.get(mode)
        if not mode_info:
            return f"Mode '{mode}' not found"

        guide = f"🔧 {mode_info.get('name', mode).upper()}\n"
        guide += f"Description: {mode_info.get('description', 'N/A')}\n\n"

        guide += "SETUP STEPS:\n"
        for step in mode_info.get("setup_steps", []):
            guide += f"  {step}\n"

        guide += "\nTROUBLESHOOTING:\n"
        for tip in mode_info.get("troubleshooting", []):
            guide += f"  • {tip}\n"

        return guide

    def get_action_guide(self, action: str) -> str:
        """Get combined guide for all modes needed for an action."""
        required_modes = self.modes_for_action(action)
        if not required_modes:
            return f"No specific mode requirements found for action: {action}"

        guide = f"ACTION: {action.upper().replace('_', ' ')}\n"
        guide += f"Required Modes: {', '.join([m.upper() for m in required_modes])}\n\n"

        for mode in required_modes:
            guide += self.format_mode_guide(mode)
            guide += "\n" + "=" * 60 + "\n\n"

        return guide
