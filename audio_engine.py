import sounddevice as sd
import numpy as np
import threading
import platform

def request_microphone_permission():
    """Request microphone permission on macOS"""
    if platform.system() == 'Darwin':  # macOS
        try:
            import subprocess
            # This will trigger the permission dialog
            subprocess.run(['osascript', '-e', 'tell application "System Events" to return'], 
                         capture_output=True, timeout=1)
        except:
            pass

SR = 44100
BLOCK = 1024

mic_input_stream = None
virtual_mic_stream = None
headphone_stream = None

config = {}
sounds = {}
lock = threading.Lock()

# Global volumes
mic_volume = 1.0
headphone_volume = 1.0
monitor_enabled = True  # Whether to hear yourself

def init(cfg, snds):
    global config, sounds
    config = cfg
    sounds = snds

def set_mic_volume(vol):
    global mic_volume
    mic_volume = float(vol)

def set_headphone_volume(vol):
    global headphone_volume
    headphone_volume = float(vol)

def set_monitor_enabled(enabled):
    global monitor_enabled
    monitor_enabled = bool(enabled)

def start():
    global mic_input_stream, virtual_mic_stream, headphone_stream
    stop()
    
    request_microphone_permission()

    if not config.get("mic") or not config.get("out"):
        return

    # Input stream - capture real microphone
    mic_input_stream = sd.InputStream(
        samplerate=SR,
        blocksize=BLOCK,
        channels=1,
        dtype="float32",
        device=config["mic"],
        callback=mic_callback
    )
    mic_input_stream.start()

    # Output stream - virtual microphone (CABLE Input or similar)
    virtual_mic_stream = sd.OutputStream(
        samplerate=SR,
        blocksize=BLOCK,
        channels=1,
        dtype="float32",
        device=config["out"],
    )
    virtual_mic_stream.start()

    # Headphone output (optional)
    if config.get("headphone_out") is not None:
        headphone_stream = sd.OutputStream(
            samplerate=SR,
            blocksize=BLOCK,
            channels=1,
            dtype="float32",
            device=config["headphone_out"]
        )
        headphone_stream.start()

def stop():
    global mic_input_stream, virtual_mic_stream, headphone_stream
    for s in (mic_input_stream, virtual_mic_stream, headphone_stream):
        if s:
            try:
                s.stop()
                s.close()
            except:
                pass
    mic_input_stream = None
    virtual_mic_stream = None
    headphone_stream = None

# Buffer to store mic input for mixing
mic_buffer = np.zeros(BLOCK, dtype="float32")
mic_buffer_lock = threading.Lock()

def mic_callback(indata, frames, time, status):
    """Capture microphone input"""
    global mic_buffer
    with mic_buffer_lock:
        mic_buffer = indata[:, 0].copy() * mic_volume

def get_sound_mix(frames):
    """Mix all playing sounds"""
    mix = np.zeros(frames, dtype="float32")
    
    with lock:
        for s in sounds.values():
            if not s["playing"]:
                continue

            start = s["pos"]
            end = start + frames
            chunk = s["data"][start:end]

            if len(chunk) < frames:
                s["playing"] = False
                s["pos"] = 0
                chunk = np.pad(chunk, (0, frames - len(chunk)))
            else:
                s["pos"] = end

            mix += chunk * s["volume"]
    
    return mix

def audio_loop():
    """Main audio loop - runs continuously"""
    global mic_buffer
    
    while virtual_mic_stream or headphone_stream:
        try:
            # Get sound mix
            sound_mix = get_sound_mix(BLOCK)
            
            # Get mic input
            with mic_buffer_lock:
                mic_data = mic_buffer.copy()
            
            # Combine mic + sounds
            combined = sound_mix + mic_data
            combined = np.clip(combined, -1, 1)
            
            # Output to virtual mic (what others hear)
            if virtual_mic_stream:
                try:
                    virtual_mic_stream.write(combined.reshape(-1, 1))
                except:
                    pass
            
            # Output to headphones (what you hear)
            if headphone_stream:
                try:
                    # Only include mic in headphone output if monitor is enabled
                    if monitor_enabled:
                        headphone_output = combined * headphone_volume
                    else:
                        # Just sounds, no mic
                        headphone_output = sound_mix * headphone_volume
                    headphone_stream.write(headphone_output.reshape(-1, 1))
                except:
                    pass
            
            # Small sleep to prevent CPU spinning
            threading.Event().wait(BLOCK / SR * 0.5)
            
        except Exception as e:
            print(f"Audio loop error: {e}")
            break

# Start audio processing thread
audio_thread = None

def start_audio_thread():
    global audio_thread
    if audio_thread is None or not audio_thread.is_alive():
        audio_thread = threading.Thread(target=audio_loop, daemon=True)
        audio_thread.start()