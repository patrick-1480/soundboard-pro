import tkinter as tk
from tkinter import filedialog, messagebox
import sounddevice as sd
import shutil
import os

from sound_manager import load_sounds
from .theme import *

SOUNDS_DIR = "sounds"


def open_settings_window(parent, config, on_apply):
    win = tk.Toplevel(parent)
    win.title("Settings")
    win.geometry("600x750")  # Made taller
    win.configure(bg=BG)
    win.grab_set()
    win.resizable(True, True)  # Made resizable so user can scroll/resize

    header = tk.Frame(win, bg=PANEL, height=70)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    header_content = tk.Frame(header, bg=PANEL)
    header_content.pack(side="left", padx=25, pady=20)
    
    tk.Label(header_content, text="SETTINGS", bg=PANEL, fg=TXT, font=("Segoe UI", 18, "bold")).pack(side="left")

    # Create scrollable content area
    canvas = tk.Canvas(win, bg=BG, highlightthickness=0)
    scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=BG)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    content = scrollable_frame
    # Add padding frame
    content_padded = tk.Frame(content, bg=BG)
    content_padded.pack(fill="both", expand=True, padx=25, pady=20)

    devices = sd.query_devices()
    inputs = [(i, d["name"]) for i, d in enumerate(devices) if d["max_input_channels"] > 0]
    outputs = [(i, d["name"]) for i, d in enumerate(devices) if d["max_output_channels"] > 0]

    mic_section = tk.Frame(content_padded, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
    mic_section.pack(fill="x", pady=(0, 15))
    
    mic_header = tk.Frame(mic_section, bg=CARD)
    mic_header.pack(fill="x", padx=20, pady=(15, 5))
    
    tk.Label(mic_header, text="Microphone Input", bg=CARD, fg=TXT, font=FONT_HEADING).pack(anchor="w")
    tk.Label(mic_header, text="Your physical microphone that you speak into", bg=CARD, fg=SUBTXT, font=FONT_SMALL).pack(anchor="w", pady=(2, 0))
    
    in_var = tk.StringVar()
    in_menu = tk.OptionMenu(mic_section, in_var, *[f"{i}: {n}" for i, n in inputs])
    in_menu.config(bg=BTN, fg=TXT, font=FONT_MAIN, highlightthickness=0, relief="flat", padx=10, pady=8)
    in_menu["menu"].config(bg=BTN, fg=TXT, font=FONT_MAIN)
    in_menu.pack(fill="x", padx=20, pady=(5, 15))

    vout_section = tk.Frame(content_padded, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
    vout_section.pack(fill="x", pady=(0, 15))
    
    vout_header = tk.Frame(vout_section, bg=CARD)
    vout_header.pack(fill="x", padx=20, pady=(15, 5))
    
    tk.Label(vout_header, text="Virtual Mic Output", bg=CARD, fg=TXT, font=FONT_HEADING).pack(anchor="w")
    tk.Label(vout_header, text="CABLE Input or virtual device (what Discord/games hear)", bg=CARD, fg=SUBTXT, font=FONT_SMALL).pack(anchor="w", pady=(2, 0))
    
    out_var = tk.StringVar()
    out_menu = tk.OptionMenu(vout_section, out_var, *[f"{i}: {n}" for i, n in outputs])
    out_menu.config(bg=BTN, fg=TXT, font=FONT_MAIN, highlightthickness=0, relief="flat", padx=10, pady=8)
    out_menu["menu"].config(bg=BTN, fg=TXT, font=FONT_MAIN)
    out_menu.pack(fill="x", padx=20, pady=(5, 15))

    hp_section = tk.Frame(content_padded, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
    hp_section.pack(fill="x", pady=(0, 15))
    
    hp_header = tk.Frame(hp_section, bg=CARD)
    hp_header.pack(fill="x", padx=20, pady=(15, 5))
    
    tk.Label(hp_header, text="Headphone Output (Optional)", bg=CARD, fg=TXT, font=FONT_HEADING).pack(anchor="w")
    tk.Label(hp_header, text="Your speakers/headphones (what you hear)", bg=CARD, fg=SUBTXT, font=FONT_SMALL).pack(anchor="w", pady=(2, 0))
    
    headphone_var = tk.StringVar()
    headphone_options = ["None (Silent)"] + [f"{i}: {n}" for i, n in outputs]
    hp_menu = tk.OptionMenu(hp_section, headphone_var, *headphone_options)
    hp_menu.config(bg=BTN, fg=TXT, font=FONT_MAIN, highlightthickness=0, relief="flat", padx=10, pady=8)
    hp_menu["menu"].config(bg=BTN, fg=TXT, font=FONT_MAIN)
    hp_menu.pack(fill="x", padx=20, pady=(5, 15))

    # Set current values or defaults
    if config.get("mic") is not None:
        try:
            in_var.set(f'{config["mic"]}: {devices[config["mic"]]["name"]}')
        except:
            if inputs:
                in_var.set(f'{inputs[0][0]}: {inputs[0][1]}')
    else:
        if inputs:
            in_var.set(f'{inputs[0][0]}: {inputs[0][1]}')
    
    if config.get("out") is not None:
        try:
            out_var.set(f'{config["out"]}: {devices[config["out"]]["name"]}')
        except:
            if outputs:
                out_var.set(f'{outputs[0][0]}: {outputs[0][1]}')
    else:
        if outputs:
            out_var.set(f'{outputs[0][0]}: {outputs[0][1]}')
    
    if config.get("headphone_out") is not None:
        try:
            headphone_var.set(f'{config["headphone_out"]}: {devices[config["headphone_out"]]["name"]}')
        except:
            headphone_var.set("None (Silent)")
    else:
        headphone_var.set("None (Silent)")

    info_box = tk.Frame(content_padded, bg=ACCENT_DARK, highlightbackground=ACCENT, highlightthickness=1)
    info_box.pack(fill="x", pady=(0, 15))
    
    info_content = tk.Frame(info_box, bg=ACCENT_DARK)
    info_content.pack(fill="x", padx=15, pady=12)
    
    tk.Label(info_content, text="💡 Quick Setup", bg=ACCENT_DARK, fg=TXT, font=FONT_BOLD).pack(anchor="w", pady=(0, 5))
    tk.Label(info_content, text="1. Virtual Mic → CABLE Input\n2. Discord/Game Mic → CABLE Output\n3. Headphones → Your actual speakers", bg=ACCENT_DARK, fg=TXT, font=FONT_SMALL, justify="left").pack(anchor="w")

    button_frame = tk.Frame(content_padded, bg=BG)
    button_frame.pack(fill="x", pady=(10, 0))

    def apply():
        try:
            # Get values from dropdowns
            mic_value = in_var.get()
            out_value = out_var.get()
            hp_value = headphone_var.get()
            
            # Validate selections
            if not mic_value or not out_value:
                messagebox.showerror("Error", "Please select both microphone and output devices!")
                return
            
            # Parse device IDs
            config["mic"] = int(mic_value.split(":")[0])
            config["out"] = int(out_value.split(":")[0])
            
            if hp_value.startswith("None"):
                config["headphone_out"] = None
            else:
                config["headphone_out"] = int(hp_value.split(":")[0])
            
            # Call the on_apply callback (this saves config and restarts audio)
            on_apply()
            win.destroy()
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid device selection. Please try again.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply settings: {str(e)}")

    cancel_btn = tk.Button(button_frame, text="Cancel", bg=BTN, fg=TXT, font=FONT_BUTTON, command=win.destroy, padx=20, pady=10)
    cancel_btn.pack(side="right", padx=(8, 0))
    style_button(cancel_btn)

    apply_btn = tk.Button(button_frame, text="Apply & Restart Audio", bg=SUCCESS_GLOW, fg=TXT, font=FONT_BUTTON, command=apply, padx=20, pady=10)
    apply_btn.pack(side="right")
    style_button(apply_btn, bg=SUCCESS_GLOW, hover_bg=SUCCESS)