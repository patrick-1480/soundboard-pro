# sound_manager.py
import os
import shutil
import tkinter.filedialog as fd
import numpy as np
import librosa

SOUNDS_DIR = "sounds"
SUPPORTED_EXTS = (".wav", ".mp3", ".ogg", ".flac")

sounds = {}
_config = {}

# Stream sample rate – set by audio_engine after querying the device.
# librosa.load(sr=TARGET_SR) handles ALL resampling correctly internally.
TARGET_SR = 48000


def set_config(cfg):
    global _config
    _config = cfg


def set_target_sr(sr: int):
    global TARGET_SR
    TARGET_SR = sr
    print(f"[sound_manager] target SR = {sr}")


def load_sounds():
    """Load all sounds from disk, resampled to TARGET_SR by librosa."""
    global sounds
    sounds.clear()
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    for file in os.listdir(SOUNDS_DIR):
        if not file.lower().endswith(SUPPORTED_EXTS):
            continue
        path = os.path.join(SOUNDS_DIR, file)
        try:
            # librosa.load with explicit sr= handles mono conversion,
            # resampling, and format decoding (including mp3) correctly.
            data, _ = librosa.load(path, sr=TARGET_SR, mono=True)
            peak = np.max(np.abs(data))
            if peak > 0:
                data = data / peak
            sounds[file] = {
                "data":     data.astype(np.float32),
                "pos":      0,
                "playing":  False,
                "volume":   1.0,
                "hotkey":   None,
            }
            duration = len(data) / TARGET_SR
            print(f"[sound] loaded {file}: {len(data)} samples at {TARGET_SR} Hz = {duration:.3f}s")
            if duration < 1.0:
                print(f"[sound] WARNING: {file} is suspiciously short!")
        except Exception as e:
            print(f"[sound] error loading {file}: {e}")


def toggle_sound(name):
    if name in sounds:
        s = sounds[name]
        s["playing"] = not s["playing"]
        s["pos"] = 0


def stop_all_sounds():
    for s in sounds.values():
        s["playing"] = False
        s["pos"] = 0


def add_sound():
    file = fd.askopenfilename(filetypes=[("Audio Files", SUPPORTED_EXTS)])
    if file:
        os.makedirs(SOUNDS_DIR, exist_ok=True)
        dst = os.path.join(SOUNDS_DIR, os.path.basename(file))
        shutil.copy2(file, dst)
        load_sounds()


def remove_sound(name):
    if name in sounds:
        path = os.path.join(SOUNDS_DIR, name)
        if os.path.exists(path):
            os.remove(path)
        sounds.pop(name)


def set_sound_volume(name, volume):
    if name in sounds:
        sounds[name]["volume"] = float(volume)


def set_hotkey(name, hotkey):
    if name in sounds:
        sounds[name]["hotkey"] = hotkey
        _register_hotkey(name, hotkey)


def remove_hotkey(name):
    if name in sounds:
        old = sounds[name].get("hotkey")
        if old:
            try:
                import keyboard
                keyboard.remove_hotkey(old)
            except Exception:
                pass
        sounds[name]["hotkey"] = None


def _register_hotkey(name, hotkey):
    try:
        import keyboard
        try:
            keyboard.remove_hotkey(hotkey)
        except Exception:
            pass
        keyboard.add_hotkey(hotkey, lambda n=name: toggle_sound(n))
    except Exception as e:
        print(f"[hotkey] could not register {hotkey}: {e}")
