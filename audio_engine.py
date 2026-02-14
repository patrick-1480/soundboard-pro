# audio_engine.py
import sounddevice as sd
import numpy as np
import threading

BLOCK = 1024

config  = {}
sounds  = {}
_lock   = threading.Lock()

_mic_stream     = None
_vmic_stream    = None
_monitor_stream = None
_monitor_enabled = True

_mic_buf      = np.zeros(BLOCK, dtype="float32")
_mic_buf_lock = threading.Lock()

SR = 48000


def init(cfg, snds):
    global config, sounds
    config = cfg
    sounds = snds


def set_monitor_enabled(enabled: bool):
    global _monitor_enabled
    _monitor_enabled = enabled


def start():
    global _mic_stream, _vmic_stream, _monitor_stream, SR

    stop()

    vmic_dev    = config.get("mic_out")
    mic_dev     = config.get("mic")
    monitor_dev = config.get("monitor_out")

    if vmic_dev is None:
        print("[audio] mic_out not set – skipping")
        return

    # Detect SR from device
    try:
        SR = int(sd.query_devices(vmic_dev)["default_samplerate"])
        print(f"[audio] device SR = {SR}")
    except Exception as e:
        print(f"[audio] SR detection failed: {e}, using {SR}")

    # Reload sounds at correct SR
    try:
        import sound_manager as _sm
        _sm.set_target_sr(SR)
        _sm.load_sounds()
        from effects import init_sound_effects
        for s in _sm.sounds.values():
            init_sound_effects(s)
        print(f"[audio] {len(_sm.sounds)} sounds loaded at {SR} Hz")
    except Exception as e:
        print(f"[audio] sound reload failed: {e}")

    # Open monitor as a raw stream we write to manually (not callback-based)
    # This way it is driven by the vmic callback — one clock, no drift.
    if monitor_dev is not None:
        try:
            _monitor_stream = sd.RawOutputStream(
                samplerate=SR, blocksize=BLOCK,
                channels=1, dtype="float32",
                device=monitor_dev)
            _monitor_stream.start()
            print(f"[audio] monitor started (device {monitor_dev})")
        except Exception as e:
            print(f"[audio] monitor failed: {e}")
            _monitor_stream = None

    # Mic input
    def _mic_cb(indata, frames, time_info, status):
        with _mic_buf_lock:
            _mic_buf[:frames] = indata[:frames, 0]

    if mic_dev is not None:
        try:
            _mic_stream = sd.InputStream(
                samplerate=SR, blocksize=BLOCK,
                channels=1, dtype="float32",
                device=mic_dev, callback=_mic_cb)
            _mic_stream.start()
            print(f"[audio] mic started (device {mic_dev})")
        except Exception as e:
            print(f"[audio] mic failed: {e}")

    # Virtual cable output — single callback, advances pos ONCE, writes to monitor too
    def _vmic_cb(outdata, frames, time_info, status):
        # Mix sounds — pos advances here only
        sound_mix = np.zeros(frames, dtype="float32")
        with _lock:
            for s in sounds.values():
                if not s.get("playing", False):
                    continue
                pos  = s["pos"]
                data = s["data"]
                chunk = data[pos: pos + frames]
                if len(chunk) < frames:
                    chunk = np.pad(chunk, (0, frames - len(chunk)))
                    s["playing"] = False
                    s["pos"]     = 0
                else:
                    s["pos"] = pos + frames
                sound_mix += chunk * float(s.get("volume", 1.0))

        # Add mic to virtual cable
        mic_vol = float(config.get("mic_volume", 1.0))
        with _mic_buf_lock:
            mic = _mic_buf[:frames] * mic_vol

        vmic_out = np.clip(sound_mix + mic, -1.0, 1.0)
        outdata[:, 0] = vmic_out

        # Write to headphones from the same callback — same clock, no drift
        if _monitor_stream is not None:
            hp_vol = float(config.get("headphone_volume", 1.0))
            if _monitor_enabled:
                hp_out = np.clip((sound_mix + mic) * hp_vol, -1.0, 1.0)
            else:
                hp_out = np.clip(sound_mix * hp_vol, -1.0, 1.0)
            try:
                _monitor_stream.write(hp_out.astype("float32").tobytes())
            except Exception:
                pass

    try:
        _vmic_stream = sd.OutputStream(
            samplerate=SR, blocksize=BLOCK,
            channels=1, dtype="float32",
            device=vmic_dev, callback=_vmic_cb)
        _vmic_stream.start()
        print(f"[audio] virtual cable started (device {vmic_dev})")
    except Exception as e:
        print(f"[audio] virtual cable failed: {e}")
        return


def stop():
    global _mic_stream, _vmic_stream, _monitor_stream
    for s in (_mic_stream, _vmic_stream, _monitor_stream):
        if s:
            try: s.stop(); s.close()
            except Exception: pass
    _mic_stream = _vmic_stream = _monitor_stream = None
    print("[audio] stopped")
