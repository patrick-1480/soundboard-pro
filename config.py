import json
import os

# Save config in user's AppData folder, not the install directory
# This works even when installed in Program Files
def get_config_dir():
    """Get the directory where config should be saved"""
    if os.name == 'nt':  # Windows
        appdata = os.getenv('APPDATA')
        config_dir = os.path.join(appdata, 'SoundboardPro')
    else:  # Mac/Linux
        home = os.path.expanduser('~')
        config_dir = os.path.join(home, '.soundboardpro')
    
    # Create directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

CONFIG_FILE = os.path.join(get_config_dir(), "config.json")

DEFAULT_CONFIG = {
    "mic": None,
    "out": None,
    "headphone_out": None,
    "mic_volume": 1.0,
    "headphone_volume": 1.0,
    "monitor_enabled": True,  # Hear yourself by default
    "sounds": {}  # Will store {filename: {volume: float, hotkey: str}}
}


def load_config():
    """Load configuration from file"""
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy()

    # Ensure all default keys exist
    for k, v in DEFAULT_CONFIG.items():
        data.setdefault(k, v)

    return data


def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def save_sound_settings(config, sounds):
    """Save all sound-specific settings (volumes, hotkeys)"""
    config["sounds"] = {}
    
    for name, sound_data in sounds.items():
        config["sounds"][name] = {
            "volume": sound_data.get("volume", 1.0),
            "hotkey": sound_data.get("hotkey", None)
        }
    
    return save_config(config)


def load_sound_settings(config, sounds):
    """Load sound-specific settings from config"""
    saved_sounds = config.get("sounds", {})
    
    for name, sound_data in sounds.items():
        if name in saved_sounds:
            sound_data["volume"] = saved_sounds[name].get("volume", 1.0)
            sound_data["hotkey"] = saved_sounds[name].get("hotkey", None)