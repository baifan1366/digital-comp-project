"""Application configuration and constants."""

import os
from pathlib import Path

try:
    from platformdirs import user_data_dir
    PLATFORMDIRS_AVAILABLE = True
except ImportError:
    PLATFORMDIRS_AVAILABLE = False


# Application metadata
APP_NAME = "StudyPlanner"
APP_AUTHOR = "StudyPlanner"
APP_VERSION = "1.0.0"


# Storage paths for different platforms
def get_default_storage_path() -> Path:
    """
    Get the default storage path for the current platform.
    
    Returns platform-specific data directory:
    - Windows: %APPDATA%/StudyPlanner/data.json
    - macOS: ~/Library/Application Support/StudyPlanner/data.json
    - Linux: ~/.local/share/StudyPlanner/data.json
    
    Falls back to current directory if platformdirs is not available.
    
    Returns:
        Path object pointing to the default storage location
    """
    if PLATFORMDIRS_AVAILABLE:
        data_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    else:
        # Fallback to platform-specific paths without platformdirs
        if os.name == 'nt':  # Windows
            appdata = os.getenv('APPDATA', os.path.expanduser('~'))
            data_dir = Path(appdata) / APP_NAME
        elif os.uname().sysname == 'Darwin':  # macOS
            data_dir = Path.home() / 'Library' / 'Application Support' / APP_NAME
        else:  # Linux and other Unix-like systems
            data_dir = Path.home() / '.local' / 'share' / APP_NAME
    
    # Create directory if it doesn't exist
    data_dir.mkdir(parents=True, exist_ok=True)
    
    return data_dir / 'data.json'


# Default storage file path
DEFAULT_STORAGE_PATH = get_default_storage_path()


# Preset plan configurations
# These match the requirements: 1.1, 1.2, 1.3
PRESET_POMODORO = {
    "name": "Pomodoro",
    "study_minutes": 25,
    "break_minutes": 5,
    "cycles": 4,
    "long_break_minutes": 15
}

PRESET_DEEP_FOCUS = {
    "name": "Deep Focus",
    "study_minutes": 50,
    "break_minutes": 10,
    "cycles": 1,
    "long_break_minutes": 0
}

PRESET_LIGHT_REVIEW = {
    "name": "Light Review",
    "study_minutes": 30,
    "break_minutes": 5,
    "cycles": 1,
    "long_break_minutes": 0
}

# All preset plans
PRESET_PLANS = [
    PRESET_POMODORO,
    PRESET_DEEP_FOCUS,
    PRESET_LIGHT_REVIEW
]


# Validation constants
MIN_TIME_MINUTES = 1
MAX_TIME_MINUTES = 180
MIN_CYCLE_COUNT = 1


# Notification settings defaults
DEFAULT_NOTIFICATION_SETTINGS = {
    "popup_enabled": True,
    "system_enabled": True,
    "sound_enabled": True
}


# History settings
MAX_HISTORY_ENTRIES = 5


# Timer settings
TIMER_TICK_INTERVAL_SECONDS = 1
UI_RESPONSE_TIME_MS = 100


# Storage settings
STORAGE_FORMAT = "json"
STORAGE_ENCODING = "utf-8"
STORAGE_INDENT = 2
