import tkinter as tk
from tkinter import messagebox
import threading
import time
import traceback
import keyboard

from config import load_config, save_config
import audio_engine
from sound_manager import sounds, load_sounds, toggle_sound, stop_all_sounds, add_sound, remove_sound, set_hotkey, remove_hotkey, set_sound_volume, set_config
from ui.settings import open_settings_window
from ui.theme import *

# --- Wrap everything in try/except to catch startup crashes ---
try:

    # =========================
    # APP INIT
    # =========================
    config = load_config()
    set_config(config)
    load_sounds()

    audio_engine.init(config, sounds)
    
    # Only start audio if devices are configured
    if config.get("mic") is not None and config.get("out") is not None:
        try:
            audio_engine.start()
            audio_engine.start_audio_thread()
        except Exception as e:
            print(f"Warning: Audio engine failed to start: {e}")
            print("You can configure audio devices in Settings")

    # =========================
    # ROOT WINDOW
    # =========================
    root = tk.Tk()
    root.title("Soundboard Pro")
    root.geometry("700x850")
    root.configure(bg=BG)
    root.resizable(True, True)

    # Loading screen
    loading_frame = tk.Frame(root, bg=BG)
    loading_frame.pack(expand=True, fill="both")
    
    tk.Label(loading_frame, text="SOUNDBOARD PRO", bg=BG, fg=ACCENT, font=("Segoe UI", 24, "bold")).pack(pady=(200, 10))
    tk.Label(loading_frame, text="Loading audio engine...", bg=BG, fg=SUBTXT, font=FONT_MAIN).pack()
    
    root.update()
    time.sleep(0.5)
    loading_frame.destroy()

    # Title bar
    title_bar = tk.Frame(root, bg=PANEL, height=60)
    title_bar.pack(fill="x", side="top")
    title_bar.pack_propagate(False)

    title_container = tk.Frame(title_bar, bg=PANEL)
    title_container.pack(side="left", padx=20, pady=15)
    
    tk.Label(title_container, text="SOUNDBOARD", bg=PANEL, fg=TXT, font=("Segoe UI", 16, "bold")).pack(side="left")
    tk.Label(title_container, text="PRO", bg=PANEL, fg=ACCENT, font=("Segoe UI", 16, "bold")).pack(side="left", padx=(5, 0))

    version_badge = tk.Label(title_bar, text="v2.0", bg=ACCENT_DARK, fg=TXT, font=FONT_SMALL, padx=8, pady=3)
    version_badge.pack(side="left", padx=(0, 10))

    # Hotkey dialog
    def open_hotkey_dialog(name, parent_refresh):
        dialog = tk.Toplevel(root)
        dialog.title("Set Hotkey")
        dialog.geometry("450x250")
        dialog.configure(bg=BG)
        dialog.transient(root)
        dialog.grab_set()

        header = tk.Frame(dialog, bg=PANEL, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(header, text="CONFIGURE HOTKEY", bg=PANEL, fg=TXT, font=FONT_HEADING).pack(side="left", padx=20, pady=20)

        content = tk.Frame(dialog, bg=BG)
        content.pack(fill="both", expand=True, padx=30, pady=20)

        tk.Label(content, text=f"Sound: {name}", bg=BG, fg=SUBTXT, font=FONT_MAIN).pack(pady=(0, 20))

        display = tk.Label(content, text="Press any key combination...", bg=CARD, fg=ACCENT, font=("Consolas", 14, "bold"), padx=30, pady=20)
        display.pack(pady=10)

        tk.Label(content, text="Press ESC to cancel", bg=BG, fg=SUBTXT_DARK, font=FONT_SMALL).pack(pady=10)

        recorded_key = {"value": None}

        def on_key(e):
            if e.event_type == "down":
                if e.name == "esc":
                    dialog.destroy()
                    return

                modifiers = []
                if keyboard.is_pressed('ctrl'):
                    modifiers.append('ctrl')
                if keyboard.is_pressed('shift'):
                    modifiers.append('shift')
                if keyboard.is_pressed('alt'):
                    modifiers.append('alt')

                key = e.name
                if key not in ['ctrl', 'shift', 'alt']:
                    if modifiers:
                        hotkey_str = '+'.join(modifiers) + '+' + key
                    else:
                        hotkey_str = key

                    recorded_key["value"] = hotkey_str
                    display.config(text=f"{hotkey_str}", fg=SUCCESS)
                    
                    dialog.after(500, lambda: apply_and_close())

        def apply_and_close():
            keyboard.unhook(hook)
            if recorded_key["value"]:
                if set_hotkey(name, recorded_key["value"]):
                    dialog.destroy()
                    parent_refresh()
                else:
                    messagebox.showerror("Error", f"Failed to set hotkey: {recorded_key['value']}")
                    dialog.destroy()
            else:
                dialog.destroy()

        hook = keyboard.hook(on_key)
        dialog.protocol("WM_DELETE_WINDOW", lambda: (keyboard.unhook(hook), dialog.destroy()))

    # Control bar
    control_bar = tk.Frame(root, bg=PANEL, height=50)
    control_bar.pack(fill="x", pady=(0, 0))
    control_bar.pack_propagate(False)

    controls_left = tk.Frame(control_bar, bg=PANEL)
    controls_left.pack(side="left", padx=15, pady=10)

    def open_settings():
        open_settings_window(parent=root, config=config, on_apply=lambda: (save_config(config), audio_engine.stop(), audio_engine.start(), audio_engine.start_audio_thread()))

    settings_btn = tk.Button(controls_left, text=f"{ICON_SETTINGS} Settings", bg=BTN, fg=TXT, font=FONT_BUTTON, command=open_settings, padx=15, pady=8)
    settings_btn.pack(side="left", padx=(0, 8))
    style_button(settings_btn)

    add_btn = tk.Button(controls_left, text=f"{ICON_ADD} Add Sound", bg=ACCENT_DARK, fg=TXT, font=FONT_BUTTON, command=lambda: (add_sound(), refresh()), padx=15, pady=8)
    add_btn.pack(side="left", padx=(0, 8))
    style_button(add_btn, bg=ACCENT_DARK, hover_bg=ACCENT)

    stop_btn = tk.Button(controls_left, text=f"{ICON_STOP} Stop All", bg=DANGER_DARK, fg=TXT, font=FONT_BUTTON, command=lambda: stop_all_sounds() or refresh(), padx=15, pady=8)
    stop_btn.pack(side="left")
    style_button(stop_btn, bg=DANGER_DARK, hover_bg=DANGER)

    # Master volume panel
    volume_container = tk.Frame(root, bg=BG)
    volume_container.pack(fill="x", padx=20, pady=(15, 10))

    volume_panel = tk.Frame(volume_container, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
    volume_panel.pack(fill="x")

    vol_header = tk.Frame(volume_panel, bg=CARD)
    vol_header.pack(fill="x", padx=20, pady=(15, 10))
    
    vol_header_left = tk.Frame(vol_header, bg=CARD)
    vol_header_left.pack(side="left")
    
    tk.Label(vol_header_left, text="MASTER CONTROLS", bg=CARD, fg=TXT, font=FONT_HEADING).pack(side="left")
    
    # Monitor toggle on the right side of header
    monitor_toggle_frame = tk.Frame(vol_header, bg=CARD)
    monitor_toggle_frame.pack(side="right")
    
    tk.Label(monitor_toggle_frame, text="Hear Myself", bg=CARD, fg=SUBTXT, font=FONT_SMALL).pack(side="left", padx=(0, 8))
    
    monitor_var = tk.BooleanVar(value=config.get("monitor_enabled", True))
    
    def toggle_monitor():
        enabled = monitor_var.get()
        audio_engine.set_monitor_enabled(enabled)
        config["monitor_enabled"] = enabled
        save_config(config)
        # Update button appearance
        if enabled:
            monitor_btn.config(bg=SUCCESS_GLOW, fg=TXT, text="ON")
            style_button(monitor_btn, bg=SUCCESS_GLOW, hover_bg=SUCCESS)
        else:
            monitor_btn.config(bg=BTN, fg=SUBTXT, text="OFF")
            style_button(monitor_btn)
    
    monitor_btn = tk.Button(
        monitor_toggle_frame,
        text="ON" if monitor_var.get() else "OFF",
        bg=SUCCESS_GLOW if monitor_var.get() else BTN,
        fg=TXT if monitor_var.get() else SUBTXT,
        font=FONT_MONO,
        command=lambda: (monitor_var.set(not monitor_var.get()), toggle_monitor()),
        width=5,
        padx=10,
        pady=4
    )
    monitor_btn.pack(side="left")
    if monitor_var.get():
        style_button(monitor_btn, bg=SUCCESS_GLOW, hover_bg=SUCCESS)
    else:
        style_button(monitor_btn)
    
    # Set initial monitor state
    audio_engine.set_monitor_enabled(monitor_var.get())

    # Mic volume
    mic_frame = tk.Frame(volume_panel, bg=CARD)
    mic_frame.pack(fill="x", padx=20, pady=(5, 10))
    
    mic_label_frame = tk.Frame(mic_frame, bg=CARD)
    mic_label_frame.pack(fill="x", pady=(0, 5))
    
    tk.Label(mic_label_frame, text="Microphone", bg=CARD, fg=TXT, font=FONT_BOLD).pack(side="left")
    
    mic_val_label = tk.Label(mic_label_frame, text="100%", bg=CARD, fg=ACCENT, font=FONT_MONO)
    mic_val_label.pack(side="right")

    mic_vol_slider = tk.Scale(mic_frame, from_=0, to=2, resolution=0.01, orient="horizontal", bg=CARD, fg=TXT, troughcolor=BTN, highlightthickness=0, showvalue=0, command=lambda v: (audio_engine.set_mic_volume(float(v)), save_mic_volume(float(v)), mic_val_label.config(text=f"{int(float(v)*100)}%")))
    mic_vol_slider.set(config.get("mic_volume", 1.0))
    mic_vol_slider.pack(fill="x")

    # Headphone volume
    hp_frame = tk.Frame(volume_panel, bg=CARD)
    hp_frame.pack(fill="x", padx=20, pady=(5, 15))
    
    hp_label_frame = tk.Frame(hp_frame, bg=CARD)
    hp_label_frame.pack(fill="x", pady=(0, 5))
    
    tk.Label(hp_label_frame, text="Headphones", bg=CARD, fg=TXT, font=FONT_BOLD).pack(side="left")
    
    hp_val_label = tk.Label(hp_label_frame, text="100%", bg=CARD, fg=ACCENT, font=FONT_MONO)
    hp_val_label.pack(side="right")

    headphone_vol_slider = tk.Scale(hp_frame, from_=0, to=2, resolution=0.01, orient="horizontal", bg=CARD, fg=TXT, troughcolor=BTN, highlightthickness=0, showvalue=0, command=lambda v: (audio_engine.set_headphone_volume(float(v)), save_headphone_volume(float(v)), hp_val_label.config(text=f"{int(float(v)*100)}%")))
    headphone_vol_slider.set(config.get("headphone_volume", 1.0))
    headphone_vol_slider.pack(fill="x")

    def save_mic_volume(vol):
        config["mic_volume"] = vol
        save_config(config)

    def save_headphone_volume(vol):
        config["headphone_volume"] = vol
        save_config(config)

    audio_engine.set_mic_volume(config.get("mic_volume", 1.0))
    audio_engine.set_headphone_volume(config.get("headphone_volume", 1.0))
    mic_val_label.config(text=f"{int(config.get('mic_volume', 1.0)*100)}%")
    hp_val_label.config(text=f"{int(config.get('headphone_volume', 1.0)*100)}%")

    # Sounds header
    sounds_header = tk.Frame(root, bg=BG)
    sounds_header.pack(fill="x", padx=20, pady=(15, 10))
    
    tk.Label(sounds_header, text="SOUNDS", bg=BG, fg=TXT, font=FONT_HEADING).pack(side="left")
    
    sound_count_label = tk.Label(sounds_header, text="0 loaded", bg=BG, fg=SUBTXT, font=FONT_SMALL)
    sound_count_label.pack(side="left", padx=(10, 0))

    # Scroll area
    canvas = tk.Canvas(root, bg=BG, highlightthickness=0)
    scroll = tk.Scrollbar(root, command=canvas.yview, bg=PANEL, troughcolor=BG)
    content = tk.Frame(canvas, bg=BG)

    canvas.create_window((0, 0), window=content, anchor="nw")
    canvas.configure(yscrollcommand=scroll.set)

    canvas.pack(side="left", fill="both", expand=True, padx=(20, 0), pady=(0, 20))
    scroll.pack(side="right", fill="y", padx=(0, 20), pady=(0, 20))

    sound_buttons = {}

    def refresh():
        for w in content.winfo_children():
            w.destroy()
        sound_buttons.clear()

        sound_count_label.config(text=f"{len(sounds)} loaded")

        if not sounds:
            empty_frame = tk.Frame(content, bg=BG)
            empty_frame.pack(expand=True, fill="both", pady=100)
            
            tk.Label(empty_frame, text="No sounds yet", bg=BG, fg=SUBTXT, font=("Segoe UI", 14)).pack()
            tk.Label(empty_frame, text=f"Click '{ICON_ADD} Add Sound' to get started", bg=BG, fg=SUBTXT_DARK, font=FONT_MAIN).pack(pady=(5, 0))
            return

        for name, s in sounds.items():
            card = tk.Frame(content, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
            card.pack(fill="x", pady=(0, 10))

            card_content = tk.Frame(card, bg=CARD)
            card_content.pack(fill="both", padx=15, pady=12)

            top_row = tk.Frame(card_content, bg=CARD)
            top_row.pack(fill="x", pady=(0, 10))

            if s["playing"]:
                btn_color = SUCCESS_GLOW
                btn_text = f"{ICON_PLAY} {name}"
                btn_fg = "#ffffff"
            else:
                btn_color = BTN
                btn_text = name
                btn_fg = TXT

            play_btn = tk.Button(top_row, text=btn_text, bg=btn_color, fg=btn_fg, font=FONT_LARGE, command=lambda n=name: (toggle_sound(n), refresh()), padx=20, pady=12, anchor="w")
            play_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))
            
            if s["playing"]:
                style_button(play_btn, bg=SUCCESS_GLOW, hover_bg=SUCCESS, active_bg=SUCCESS_GLOW)
            else:
                style_button(play_btn)
            
            sound_buttons[name] = play_btn

            del_btn = tk.Button(top_row, text=ICON_DELETE, bg=DANGER_DARK, fg=TXT, font=("Segoe UI", 14, "bold"), command=lambda n=name: (remove_sound(n), refresh()), width=3, padx=10, pady=12)
            del_btn.pack(side="right")
            style_button(del_btn, bg=DANGER_DARK, hover_bg=DANGER)

            hotkey_row = tk.Frame(card_content, bg=CARD)
            hotkey_row.pack(fill="x", pady=(0, 10))

            tk.Label(hotkey_row, text="Hotkey", bg=CARD, fg=SUBTXT, font=FONT_SMALL).pack(side="left")

            hotkey_display = s["hotkey"] if s["hotkey"] else "Not set"
            hotkey_label = tk.Label(hotkey_row, text=hotkey_display, bg=BTN, fg=ACCENT if s["hotkey"] else SUBTXT, font=FONT_MONO, padx=10, pady=4)
            hotkey_label.pack(side="left", padx=(10, 8))

            set_hotkey_btn = tk.Button(hotkey_row, text=f"{ICON_KEYBOARD} {'Change' if s['hotkey'] else 'Set'}", bg=BTN, fg=TXT, font=FONT_SMALL, command=lambda n=name: open_hotkey_dialog(n, refresh), padx=10, pady=4)
            set_hotkey_btn.pack(side="left", padx=(0, 4))
            style_button(set_hotkey_btn)

            if s["hotkey"]:
                clear_btn = tk.Button(hotkey_row, text=ICON_CLEAR, bg=DANGER_DARK, fg=TXT, font=FONT_SMALL, command=lambda n=name: (remove_hotkey(n), refresh()), padx=8, pady=4)
                clear_btn.pack(side="left")
                style_button(clear_btn, bg=DANGER_DARK, hover_bg=DANGER)

            vol_row = tk.Frame(card_content, bg=CARD)
            vol_row.pack(fill="x")

            vol_label_frame = tk.Frame(vol_row, bg=CARD)
            vol_label_frame.pack(fill="x", pady=(0, 5))
            
            tk.Label(vol_label_frame, text="Volume", bg=CARD, fg=SUBTXT, font=FONT_SMALL).pack(side="left")
            
            vol_val_label = tk.Label(vol_label_frame, text=f"{int(s['volume']*100)}%", bg=CARD, fg=ACCENT, font=FONT_MONO)
            vol_val_label.pack(side="right")

            vol = tk.Scale(vol_row, from_=0, to=2, resolution=0.01, orient="horizontal", bg=CARD, fg=TXT, troughcolor=BTN, highlightthickness=0, showvalue=0)
            vol.set(s["volume"])

            def set_vol(val, n=name, label=vol_val_label):
                set_sound_volume(n, float(val))
                label.config(text=f"{int(float(val)*100)}%")

            vol.config(command=set_vol)
            vol.pack(fill="x")

    def auto_refresh_buttons():
        for name, btn in sound_buttons.items():
            if name in sounds:
                s = sounds[name]
                if s["playing"]:
                    if btn['bg'] != SUCCESS_GLOW:
                        btn.config(bg=SUCCESS_GLOW, text=f"{ICON_PLAY} {name}", fg="#ffffff")
                else:
                    if btn['bg'] != BTN:
                        btn.config(bg=BTN, text=name, fg=TXT)
        root.after(100, auto_refresh_buttons)

    content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    refresh()
    auto_refresh_buttons()

    if config.get("mic") is None or config.get("out") is None:
        root.after(300, lambda: messagebox.showinfo("Welcome to Soundboard Pro", "Let's configure your audio devices to get started.") or open_settings())

    def on_close():
        save_config(config)
        keyboard.unhook_all()
        audio_engine.stop()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

except Exception as e:
    import traceback
    print("ERROR OCCURRED:")
    traceback.print_exc()
    
    # Show error dialog instead of input() which doesn't work in GUI apps
    try:
        from tkinter import messagebox
        root_error = tk.Tk()
        root_error.withdraw()
        messagebox.showerror(
            "Soundboard Pro - Startup Error",
            f"Failed to start application:\n\n{str(e)}\n\nMake sure VB-Audio Cable is installed.\n\nCheck console for details."
        )
        root_error.destroy()
    except:
        pass  # If even the error dialog fails, just exit