# sound_manager.py
import os
import json
import tkinter.filedialog as fd
import librosa
import numpy as np
import keyboard

# Get proper sounds directory in user's AppData
def get_sounds_dir():
    """Get the directory where sounds should be stored"""
    if os.name == 'nt':  # Windows
        appdata = os.getenv('APPDATA')
        sounds_dir = os.path.join(appdata, 'SoundboardPro', 'sounds')
    else:  # Mac/Linux
        home = os.path.expanduser('~')
        sounds_dir = os.path.join(home, '.soundboardpro', 'sounds')
    
    # Create directory if it doesn't exist
    os.makedirs(sounds_dir, exist_ok=True)
    return sounds_dir

SOUNDS_DIR = get_sounds_dir()
SUPPORTED_EXTS = (".wav", ".mp3", ".ogg", ".flac")

sounds = {}
registered_hotkeys = {}
config = None  # Will be set by app

def set_config(cfg):
    """Set the config reference so we can save changes"""
    global config
    config = cfg

# -------------------------
# LOAD / RELOAD SOUNDS
# -------------------------
def load_sounds():
    global sounds
    sounds.clear()
    clear_all_hotkeys()
    
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    for file in os.listdir(SOUNDS_DIR):
        if not file.lower().endswith(SUPPORTED_EXTS):
            continue
        path = os.path.join(SOUNDS_DIR, file)
        try:
            data, _ = librosa.load(path, sr=44100, mono=True)
            peak = np.max(np.abs(data))
            if peak > 0:
                data /= peak
            sounds[file] = {
                "data": data.astype(np.float32), 
                "pos": 0, 
                "playing": False, 
                "volume": 1.0, 
                "hotkey": None
            }
        except Exception as e:
            print(f"Error loading {file}: {e}")
    
    # Load saved settings from config
    if config and "sounds" in config:
        from config import load_sound_settings
        load_sound_settings(config, sounds)
        
        # Re-register hotkeys
        for name, sound in sounds.items():
            if sound.get("hotkey"):
                set_hotkey(name, sound["hotkey"], save=False)

def save_all_settings():
    """Save all sound settings to config"""
    if config:
        from config import save_sound_settings
        save_sound_settings(config, sounds)

# -------------------------
# HOTKEY MANAGEMENT
# -------------------------
def set_hotkey(name, hotkey_str, save=True):
    """Set a global hotkey for a sound"""
    if name not in sounds:
        return False
    
    # Remove old hotkey if exists
    if sounds[name]["hotkey"]:
        remove_hotkey(name, save=False)
    
    if not hotkey_str or hotkey_str.strip() == "":
        sounds[name]["hotkey"] = None
        if save:
            save_all_settings()
        return True
    
    try:
        # Register the hotkey
        keyboard.add_hotkey(hotkey_str, lambda n=name: toggle_sound(n), suppress=True)
        sounds[name]["hotkey"] = hotkey_str
        registered_hotkeys[hotkey_str] = name
        
        if save:
            save_all_settings()
        return True
    except Exception as e:
        print(f"Failed to register hotkey {hotkey_str}: {e}")
        return False

def remove_hotkey(name, save=True):
    """Remove hotkey for a sound"""
    if name not in sounds:
        return
    
    hotkey_str = sounds[name]["hotkey"]
    if hotkey_str and hotkey_str in registered_hotkeys:
        try:
            keyboard.remove_hotkey(hotkey_str)
            del registered_hotkeys[hotkey_str]
        except:
            pass
    sounds[name]["hotkey"] = None
    
    if save:
        save_all_settings()

def clear_all_hotkeys():
    """Clear all registered hotkeys"""
    global registered_hotkeys
    try:
        keyboard.unhook_all_hotkeys()
        registered_hotkeys.clear()
    except:
        pass

# -------------------------
# VOLUME MANAGEMENT
# -------------------------
def set_sound_volume(name, volume):
    """Set volume for a specific sound and save"""
    if name in sounds:
        sounds[name]["volume"] = float(volume)
        save_all_settings()

# -------------------------
# TOGGLE SOUND
# -------------------------
def toggle_sound(name):
    if name in sounds:
        s = sounds[name]
        s["playing"] = not s["playing"]
        s["pos"] = 0

# -------------------------
# STOP ALL SOUNDS
# -------------------------
def stop_all_sounds():
    for s in sounds.values():
        s["playing"] = False
        s["pos"] = 0

# -------------------------
# ADD SOUND
# -------------------------
def add_sound():
    file = fd.askopenfilename(filetypes=[("Audio Files", SUPPORTED_EXTS)])
    if file:
        dst = os.path.join(SOUNDS_DIR, os.path.basename(file))
        try:
            os.replace(file, dst)
        except:
            import shutil
            shutil.copy(file, dst)
        load_sounds()

# -------------------------
# DELETE SOUND
# -------------------------
def delete_sound(name):
    if name in sounds:
        remove_hotkey(name, save=False)
        path = os.path.join(SOUNDS_DIR, name)
        if os.path.exists(path):
            os.remove(path)
        sounds.pop(name)
        save_all_settings()

# Alias for consistency with app.py
def remove_sound(name):
    delete_sound(name)