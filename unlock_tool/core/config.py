import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

APP_NAME = 'unlock_tool'
CONFIG_FILE_NAME = 'config.json'


def get_app_data_dir() -> Path:
    """Return the application data directory for the current platform."""
    if os.name == 'nt':
        base = os.getenv('APPDATA', Path.home() / 'AppData' / 'Roaming')
    elif sys.platform == 'darwin':
        base = Path.home() / 'Library' / 'Application Support'
    else:
        base = Path.home() / '.local' / 'share'
    return Path(base) / APP_NAME


def get_config_path() -> Path:
    """Return the path to the stored config file."""
    data_dir = get_app_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir / CONFIG_FILE_NAME


def load_config() -> Dict[str, Any]:
    """Load the application config from disk."""
    config_path = get_config_path()
    if not config_path.exists():
        return {}
    try:
        with config_path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(config: Dict[str, Any]) -> bool:
    """Save the application config to disk."""
    try:
        config_path = get_config_path()
        with config_path.open('w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception:
        return False


def has_accepted_eula() -> bool:
    """Return whether the user has accepted the EULA."""
    return load_config().get('eula_accepted', False)


def set_eula_accepted(accepted: bool = True) -> bool:
    """Persist the EULA acceptance flag."""
    config = load_config()
    config['eula_accepted'] = accepted
    return save_config(config)
