# effects.py
# Effects are stored as flags on the sound dict and applied in real-time during mixing.
# Nothing is permanently baked into the audio data.
# sound["effects"] = {"fade_in": True, "fade_out": False, "echo": True, ...}
# sound["effect_params"] = {"echo_delay": 0.3, "echo_decay": 0.5, ...}

import numpy as np

def _SR():
    try:
        import sound_manager as _sm
        return _sm.TARGET_SR
    except Exception:
        return 48000

# All available effects
EFFECTS = {
    "fade_in":   "Fade In",
    "fade_out":  "Fade Out",
    "normalize": "Normalize",
    "echo":      "Echo",
    "compress":  "Compress",
    "speed_up":  "Speed ×1.5",
    "slow_down": "Speed ×0.75",
}


def init_sound_effects(sound: dict):
    """Add effects fields to a sound dict if missing."""
    if "effects" not in sound:
        sound["effects"] = {k: False for k in EFFECTS}
    if "effect_params" not in sound:
        sound["effect_params"] = {
            "echo_delay": 0.3,
            "echo_decay": 0.5,
            "fade_duration": 0.5,
        }
    if "original_data" not in sound:
        # Keep a clean copy of the original so we can re-process any time
        sound["original_data"] = sound["data"].copy()


def get_active_effects(sound: dict) -> list:
    """Return list of effect keys that are currently enabled."""
    return [k for k, v in sound.get("effects", {}).items() if v]


def toggle_effect(sound: dict, effect_key: str) -> bool:
    """Toggle an effect on/off. Returns new state."""
    init_sound_effects(sound)
    current = sound["effects"].get(effect_key, False)
    sound["effects"][effect_key] = not current
    # Rebuild processed audio
    _rebuild(sound)
    sound["pos"] = 0
    return not current


def set_effect(sound: dict, effect_key: str, enabled: bool):
    """Explicitly set an effect on or off."""
    init_sound_effects(sound)
    sound["effects"][effect_key] = enabled
    _rebuild(sound)
    sound["pos"] = 0


def set_effect_param(sound: dict, param: str, value):
    """Update an effect parameter and rebuild."""
    init_sound_effects(sound)
    sound["effect_params"][param] = value
    _rebuild(sound)
    sound["pos"] = 0


def _rebuild(sound: dict):
    """Re-apply all active effects to original_data and store in data."""
    init_sound_effects(sound)
    data = sound["original_data"].copy()
    params = sound["effect_params"]

    if sound["effects"].get("normalize"):
        peak = np.max(np.abs(data))
        if peak > 0:
            data = data * (0.95 / peak)

    if sound["effects"].get("compress"):
        threshold, ratio = 0.5, 4.0
        mask = np.abs(data) > threshold
        sign = np.sign(data[mask])
        excess = np.abs(data[mask]) - threshold
        data[mask] = sign * (threshold + excess / ratio)

    if sound["effects"].get("echo"):
        delay_s = float(params.get("echo_delay", 0.3))
        decay   = float(params.get("echo_decay",  0.5))
        d_smp   = int(delay_s * _SR())
        out     = np.zeros(len(data) + d_smp, dtype="float32")
        out[:len(data)] += data
        out[d_smp:]     += data * decay
        data = out[:len(data)]

    if sound["effects"].get("speed_up"):
        indices = np.arange(0, len(data), 1.5)
        indices = indices[indices < len(data)]
        data = np.interp(indices, np.arange(len(data)), data).astype("float32")

    elif sound["effects"].get("slow_down"):
        indices = np.arange(0, len(data), 0.75)
        indices = indices[indices < len(data)]
        data = np.interp(indices, np.arange(len(data)), data).astype("float32")

    if sound["effects"].get("fade_in"):
        smp = min(int(float(params.get("fade_duration", 0.5)) * _SR()), len(data))
        data[:smp] *= np.linspace(0, 1, smp)

    if sound["effects"].get("fade_out"):
        smp = min(int(float(params.get("fade_duration", 0.5)) * _SR()), len(data))
        data[-smp:] *= np.linspace(1, 0, smp)

    sound["data"] = data.astype("float32")


# ─────────────────────────────────────────────────────────────
# Audio-editor helpers (non-destructive trim applied to original_data)
# ─────────────────────────────────────────────────────────────

def trim_sound(sound: dict, start_sec: float, end_sec: float):
    """Trim original_data to [start_sec, end_sec] and rebuild."""
    init_sound_effects(sound)
    original = sound["original_data"]
    s = max(0, int(start_sec * _SR()))
    e = min(len(original), int(end_sec * _SR()))
    if e > s:
        sound["original_data"] = original[s:e].copy()
        _rebuild(sound)
        sound["pos"] = 0


def reset_trim(sound: dict, raw_data: np.ndarray):
    """Restore the full original audio data (undo all trims)."""
    sound["original_data"] = raw_data.copy()
    _rebuild(sound)
    sound["pos"] = 0
