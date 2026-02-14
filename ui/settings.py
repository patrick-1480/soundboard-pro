# ui/settings.py
import tkinter as tk
from tkinter import messagebox
import traceback
import sounddevice as sd
import themes as T


def _c(name):
    return getattr(T, name)


def open_settings_window(parent, config, on_apply):

    win = tk.Toplevel(parent)
    win.title("Settings")
    win.geometry("560x660")
    win.configure(bg=_c("BG"))
    win.grab_set()
    win.resizable(True, True)

    # ── Header ───────────────────────────────────────────────
    hdr = tk.Frame(win, bg=_c("PANEL"), height=60)
    hdr.pack(fill="x"); hdr.pack_propagate(False)
    tk.Label(hdr, text="SETTINGS",
             bg=_c("PANEL"), fg=_c("TXT"),
             font=("Segoe UI", 15, "bold")).pack(side="left", padx=22, pady=18)

    # ── Scrollable body ──────────────────────────────────────
    canvas    = tk.Canvas(win, bg=_c("BG"), highlightthickness=0)
    scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
    sf        = tk.Frame(canvas, bg=_c("BG"))

    sf.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    win_id = canvas.create_window((0, 0), window=sf, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))

    # Mouse-wheel scrolling
    def _scroll(e):   canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")
    def _scroll_up(e): canvas.yview_scroll(-1, "units")
    def _scroll_dn(e): canvas.yview_scroll( 1, "units")

    def _bind_w(w):
        w.bind("<MouseWheel>", _scroll,    add="+")
        w.bind("<Button-4>",   _scroll_up, add="+")
        w.bind("<Button-5>",   _scroll_dn, add="+")

    _bind_w(canvas); _bind_w(sf); _bind_w(win)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    body = tk.Frame(sf, bg=_c("BG"))
    body.pack(fill="both", expand=True, padx=22, pady=18)
    _bind_w(body)

    # ── Query audio devices ───────────────────────────────────
    try:
        devices = sd.query_devices()
        inputs  = [(i, d["name"]) for i, d in enumerate(devices)
                   if d["max_input_channels"]  > 0]
        outputs = [(i, d["name"]) for i, d in enumerate(devices)
                   if d["max_output_channels"] > 0]
    except Exception as e:
        messagebox.showerror("Device Error",
                             f"Could not query audio devices:\n{e}", parent=win)
        win.destroy(); return

    # ── Helper: section card ──────────────────────────────────
    def _section(title, hint=""):
        f = tk.Frame(body, bg=_c("CARD"),
                     highlightbackground=_c("BORDER"), highlightthickness=1)
        f.pack(fill="x", pady=(0, 12))
        hf = tk.Frame(f, bg=_c("CARD")); hf.pack(fill="x", padx=16, pady=(12, 4))
        tk.Label(hf, text=title,
                 bg=_c("CARD"), fg=_c("TXT"), font=_c("FONT_HEADING")).pack(anchor="w")
        if hint:
            tk.Label(hf, text=hint,
                     bg=_c("CARD"), fg=_c("SUBTXT"), font=_c("FONT_SMALL")).pack(anchor="w", pady=(2, 0))
        _bind_w(f); _bind_w(hf)
        return f

    # ── Helper: dropdown ─────────────────────────────────────
    def _dropdown(parent, var, options):
        if not options:
            options = ["(no devices found)"]
        om = tk.OptionMenu(parent, var, *options)
        om.config(bg=_c("BTN"), fg=_c("TXT"), font=_c("FONT_MAIN"),
                  highlightthickness=0, relief="flat",
                  activebackground=_c("BTN_HOVER"), padx=10, pady=8)
        om["menu"].config(bg=_c("BTN"), fg=_c("TXT"), font=_c("FONT_MAIN"),
                          activebackground=_c("BTN_HOVER"))
        om.pack(fill="x", padx=16, pady=(4, 12))
        _bind_w(om)
        return om

    # ── Helper: pre-select saved device ──────────────────────
    def _restore(var, saved_id):
        if saved_id is None: return
        try:
            var.set(f"{saved_id}: {devices[saved_id]['name']}")
        except Exception:
            pass

    # ── THEME ─────────────────────────────────────────────────
    THEME_LABELS = {
        "dark":   "🌑  Dark Mode",
        "light":  "☀️   Light Mode",
        "purple": "💜  Purple Dream",
    }
    REV_THEME = {v: k for k, v in THEME_LABELS.items()}

    sec_theme = _section("Theme", "Colour scheme — applied when you click Save")
    theme_var = tk.StringVar(value=THEME_LABELS.get(config.get("theme", "dark"),
                                                     "🌑  Dark Mode"))
    _dropdown(sec_theme, theme_var, list(THEME_LABELS.values()))

    # ── MICROPHONE INPUT ──────────────────────────────────────
    sec_mic = _section("Microphone Input",
                       "Your physical mic — what you speak into")
    mic_var = tk.StringVar()
    _dropdown(sec_mic, mic_var, [f"{i}: {n}" for i, n in inputs])
    _restore(mic_var, config.get("mic"))

    # ── VIRTUAL-CABLE OUTPUT  (mic_out) ───────────────────────
    sec_vmic = _section("Virtual Mic Output  (mic_out)",
                        "CABLE Input — what Discord / your game hears")
    micout_var = tk.StringVar()
    _dropdown(sec_vmic, micout_var, [f"{i}: {n}" for i, n in outputs])
    _restore(micout_var, config.get("mic_out"))

    # ── HEADPHONE MONITOR  (monitor_out, optional) ────────────
    sec_hp = _section("Headphone Monitor  (monitor_out)  — optional",
                      "Your speakers / headphones — what YOU hear")
    monout_var = tk.StringVar()
    hp_opts = ["None (disabled)"] + [f"{i}: {n}" for i, n in outputs]
    _dropdown(sec_hp, monout_var, hp_opts)
    saved_mon = config.get("monitor_out")
    if saved_mon is not None:
        _restore(monout_var, saved_mon)
    else:
        monout_var.set("None (disabled)")

    # ── INFO BOX ──────────────────────────────────────────────
    info = tk.Frame(body, bg=_c("ACCENT_DARK"),
                    highlightbackground=_c("ACCENT"), highlightthickness=1)
    info.pack(fill="x", pady=(0, 12))
    ic = tk.Frame(info, bg=_c("ACCENT_DARK")); ic.pack(fill="x", padx=14, pady=10)
    _bind_w(info); _bind_w(ic)
    tk.Label(ic, text="💡  Quick Setup Guide",
             bg=_c("ACCENT_DARK"), fg=_c("TXT"), font=_c("FONT_HEADING")).pack(anchor="w", pady=(0, 5))
    tk.Label(ic,
             text="1.  Mic Input        →  your physical microphone\n"
                  "2.  Virtual Mic Out  →  CABLE Input (VB-Audio)\n"
                  "3.  Headphone Out    →  your real speakers / headphones\n"
                  "4.  Discord / game   →  set input device to  CABLE Output",
             bg=_c("ACCENT_DARK"), fg=_c("TXT"), font=_c("FONT_SMALL"),
             justify="left").pack(anchor="w")

    # ── SAVE / CANCEL ─────────────────────────────────────────
    bf = tk.Frame(body, bg=_c("BG")); bf.pack(fill="x", pady=(4, 0))

    def _apply():
        try:
            # ── Theme
            chosen_label = theme_var.get()
            new_theme    = REV_THEME.get(chosen_label, "dark")
            config["theme"] = new_theme

            # ── Mic input device
            mv = mic_var.get()
            if mv and not mv.startswith("(no"):
                config["mic"] = int(mv.split(":")[0])

            # ── Virtual-cable output  (mic_out)
            ov = micout_var.get()
            if not ov or ov.startswith("(no"):
                messagebox.showwarning(
                    "Missing Device",
                    "Please select a Virtual Mic Output device.\n"
                    "(Usually 'CABLE Input')", parent=win)
                return
            config["mic_out"] = int(ov.split(":")[0])

            # ── Headphone monitor  (monitor_out)
            hv = monout_var.get()
            config["monitor_out"] = (
                None if hv.startswith("None")
                else int(hv.split(":")[0])
            )

            # Apply the new theme NOW before on_apply rebuilds the UI
            T.set_theme(new_theme)

            on_apply()    # saves config, restarts audio, rebuilds full UI
            win.destroy()

        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Settings Error",
                                 f"Could not apply settings:\n{e}", parent=win)

    can_btn = tk.Button(bf, text="Cancel", bg=_c("BTN"), fg=_c("TXT"),
                        font=_c("FONT_BUTTON"), command=win.destroy,
                        padx=18, pady=10)
    can_btn.pack(side="right", padx=(8, 0))
    T.style_button(can_btn)

    sav_btn = tk.Button(bf, text="Save & Restart Audio",
                        bg=_c("SUCCESS_GLOW"), fg="white",
                        font=_c("FONT_BUTTON"), command=_apply,
                        padx=18, pady=10)
    sav_btn.pack(side="right")
    T.style_button(sav_btn, bg=_c("SUCCESS_GLOW"), hover_bg=_c("SUCCESS"))
