# app.py  –  Soundboard Pro
import tkinter as tk
from tkinter import messagebox
import traceback, os, shutil

from config  import load_config, save_config
from version import __version__
import themes as T

from effects import init_sound_effects, get_active_effects, toggle_effect, EFFECTS

_ae = None
_sm = None
sounds = {}

config   = None
root     = None
_current_refresh = None


def _c(n): return getattr(T, n)


# ─────────────────────────────────────────────────────────────
# LAZY LOADING
# ─────────────────────────────────────────────────────────────
def _load_modules():
    global _ae, _sm, sounds
    import audio_engine as ae;  _ae = ae
    import sound_manager as sm; _sm = sm
    sounds = sm.sounds
    globals()["sounds"] = sounds


def _init_audio():
    if not (_ae and _sm): return
    try:
        _sm.set_config(config)
        # Detect device SR FIRST so sounds are loaded at the right rate.
        if config.get("mic_out") is not None:
            try:
                import sounddevice as _sd
                dev_info = _sd.query_devices(config["mic_out"])
                detected_sr = int(dev_info["default_samplerate"])
                _sm.set_target_sr(detected_sr)
                print(f"[init] device SR detected early: {detected_sr}")
            except Exception as e:
                print(f"[init] SR pre-detection failed: {e}")
        _sm.load_sounds()
        for s in _sm.sounds.values():
            init_sound_effects(s)
        globals()["sounds"] = _sm.sounds
        _ae.init(config, _sm.sounds)
        if config.get("mic_out") is not None:
            _ae.start()
    except Exception:
        traceback.print_exc()


# ─────────────────────────────────────────────────────────────
# SCROLL
# ─────────────────────────────────────────────────────────────
def _bind_scroll(canvas, widget=None):
    t = widget if widget else canvas
    def _s(e): canvas.yview_scroll(int(-1*(e.delta/120)), "units")
    t.bind("<MouseWheel>", _s, add="+")
    t.bind("<Button-4>",   lambda e: canvas.yview_scroll(-1, "units"), add="+")
    t.bind("<Button-5>",   lambda e: canvas.yview_scroll( 1, "units"), add="+")


# ─────────────────────────────────────────────────────────────
# DRAG AND DROP
# ─────────────────────────────────────────────────────────────
def _setup_drag_drop(widget):
    try:
        def _drop(event):
            imported = 0
            for fp in root.tk.splitlist(event.data):
                if fp.lower().endswith((".mp3",".wav",".ogg",".flac")):
                    try:
                        os.makedirs(_sm.SOUNDS_DIR, exist_ok=True)
                        shutil.copy2(fp, os.path.join(_sm.SOUNDS_DIR, os.path.basename(fp)))
                        imported += 1
                    except Exception as e: print(f"[drop] {e}")
            if imported:
                _sm.load_sounds()
                for s in _sm.sounds.values(): init_sound_effects(s)
                globals()["sounds"] = _sm.sounds
                if _current_refresh: _current_refresh()
                messagebox.showinfo("Imported", f"Imported {imported} file(s)!")
        widget.drop_target_register("DND_Files")
        widget.dnd_bind("<<Drop>>", _drop)
    except Exception: pass


# ─────────────────────────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────────────────────────
def _open_settings():
    from ui.settings import open_settings_window
    def _on_apply():
        save_config(config)
        T.set_theme(config.get("theme", "dark"))
        if _ae:
            try: _ae.start()
            except Exception as e: print(f"[audio] restart: {e}")
        build_main_app()
    open_settings_window(parent=root, config=config, on_apply=_on_apply)


# ─────────────────────────────────────────────────────────────
# HOTKEY DIALOG
# ─────────────────────────────────────────────────────────────
def _hotkey_dialog(sound_name, callback):
    dlg = tk.Toplevel(root)
    dlg.title(f"Set Hotkey – {sound_name}")
    dlg.geometry("420x210")
    dlg.configure(bg=_c("BG"))
    dlg.grab_set(); dlg.resizable(False, False)

    tk.Label(dlg, text=f"Set hotkey for:  {sound_name}",
             bg=_c("BG"), fg=_c("TXT"), font=_c("FONT_HEADING")).pack(pady=(26, 4))
    tk.Label(dlg, text="Press any key combination…",
             bg=_c("BG"), fg=_c("SUBTXT"), font=_c("FONT_MAIN")).pack()
    res = tk.Label(dlg, text="—", bg=_c("BG"), fg=_c("ACCENT"), font=_c("FONT_MONO"))
    res.pack(pady=10)
    captured = [None]

    def _key(ev):
        if ev.keysym in ("Shift_L","Shift_R","Control_L","Control_R","Alt_L","Alt_R"): return
        mods = []
        if ev.state & 0x0001: mods.append("shift")
        if ev.state & 0x0004: mods.append("ctrl")
        if ev.state & 0x0008: mods.append("alt")
        captured[0] = "+".join(mods + [ev.keysym.lower()])
        res.config(text=captured[0])

    dlg.bind("<Key>", _key)
    bf = tk.Frame(dlg, bg=_c("BG")); bf.pack(pady=12)

    def _save():
        if captured[0]:
            _sm.set_hotkey(sound_name, captured[0])
            save_config(config); dlg.destroy(); callback()

    sb = tk.Button(bf, text="Save", bg=_c("SUCCESS"), fg="white",
                   font=_c("FONT_BUTTON"), command=_save, padx=22, pady=8)
    sb.pack(side="left", padx=6)
    T.style_button(sb, bg=_c("SUCCESS"), hover_bg=_c("SUCCESS_GLOW"))
    cb = tk.Button(bf, text="Cancel", bg=_c("BTN"), fg=_c("TXT"),
                   font=_c("FONT_BUTTON"), command=dlg.destroy, padx=22, pady=8)
    cb.pack(side="left", padx=6)
    T.style_button(cb)


# ─────────────────────────────────────────────────────────────
# EFFECT TOGGLE POPUP  (from main cards – no audio restart)
# ─────────────────────────────────────────────────────────────
def _effect_popup(sound_name, anchor_btn, refresh_badges):
    """Small popup to toggle effects directly from the sound card."""
    if sound_name not in (_sm.sounds if _sm else sounds):
        return
    sound = (_sm.sounds if _sm else sounds)[sound_name]
    init_sound_effects(sound)

    popup = tk.Toplevel(root)
    popup.overrideredirect(True)
    popup.configure(bg=_c("CARD"))
    popup.attributes("-topmost", True)

    x = anchor_btn.winfo_rootx()
    y = anchor_btn.winfo_rooty() + anchor_btn.winfo_height() + 2
    popup.geometry(f"+{x}+{y}")

    title = tk.Frame(popup, bg=_c("PANEL"))
    title.pack(fill="x")
    tk.Label(title, text=f"  Effects – {sound_name}",
             bg=_c("PANEL"), fg=_c("TXT"), font=_c("FONT_BOLD"),
             padx=10, pady=8).pack(side="left")
    tk.Button(title, text="×", bg=_c("PANEL"), fg=_c("TXT"),
              font=_c("FONT_BOLD"), command=popup.destroy,
              relief="flat", padx=8, pady=4).pack(side="right")

    body = tk.Frame(popup, bg=_c("CARD")); body.pack(fill="both", padx=8, pady=8)

    btn_refs = {}

    def _toggle(k):
        new_state = toggle_effect(sound, k)
        lbl = EFFECTS[k]
        btn_refs[k].config(
            text=f"✓  {lbl}" if new_state else f"○  {lbl}",
            bg=_c("SUCCESS_GLOW") if new_state else _c("BTN"),
            fg="white" if new_state else _c("TXT"),
        )
        refresh_badges(sound_name)   # update badge row on the card

    for k, lbl in EFFECTS.items():
        active = sound["effects"].get(k, False)
        b = tk.Button(body,
                      text=f"✓  {lbl}" if active else f"○  {lbl}",
                      bg=_c("SUCCESS_GLOW") if active else _c("BTN"),
                      fg="white" if active else _c("TXT"),
                      font=_c("FONT_SMALL"), anchor="w",
                      padx=12, pady=6, width=18,
                      command=lambda key=k: _toggle(key))
        b.pack(fill="x", pady=1)
        T.style_button(b,
                       bg=_c("SUCCESS_GLOW") if active else _c("BTN"),
                       hover_bg=_c("SUCCESS") if active else _c("BTN_HOVER"))
        btn_refs[k] = b

    # Close when clicking outside
    def _focus_out(e):
        try:
            if popup.winfo_exists():
                popup.destroy()
        except Exception: pass
    popup.bind("<FocusOut>", _focus_out)
    popup.focus_set()


# ─────────────────────────────────────────────────────────────
# MAIN UI
# ─────────────────────────────────────────────────────────────
def build_main_app():
    global _current_refresh

    for w in root.winfo_children():
        w.destroy()

    T.set_theme(config.get("theme", "dark"))
    root.configure(bg=_c("BG"))

    # ── TOP BAR ──────────────────────────────────────────────
    topbar = tk.Frame(root, bg=_c("PANEL"), height=58)
    topbar.pack(fill="x"); topbar.pack_propagate(False)
    inn = tk.Frame(topbar, bg=_c("PANEL"))
    inn.pack(fill="both", expand=True, padx=20, pady=12)

    tf = tk.Frame(inn, bg=_c("PANEL")); tf.pack(side="left")
    tk.Label(tf, text="SOUNDBOARD PRO", bg=_c("PANEL"), fg=_c("TXT"),
             font=("Segoe UI", 15, "bold")).pack(side="left")
    tk.Label(tf, text=f"  v{__version__}", bg=_c("PANEL"), fg=_c("ACCENT"),
             font=("Segoe UI", 9)).pack(side="left")

    bf = tk.Frame(inn, bg=_c("PANEL")); bf.pack(side="right")

    def _add():
        _sm.add_sound()
        for s in _sm.sounds.values(): init_sound_effects(s)
        globals()["sounds"] = _sm.sounds
        if _current_refresh: _current_refresh()

    def _stopall():
        _sm.stop_all_sounds()
        if _current_refresh: _current_refresh()

    for txt, cmd, bg_n, hov_n in [
        ("⚙  Settings",   _open_settings, "BTN",         "BTN_HOVER"),
        ("+  Add Sound",  _add,            "BTN",         "BTN_HOVER"),
        ("■  Stop All",   _stopall,        "DANGER_DARK", "DANGER"),
    ]:
        b = tk.Button(bf, text=txt, bg=_c(bg_n), fg=_c("TXT"),
                      font=_c("FONT_BUTTON"), command=cmd, padx=14, pady=8)
        b.pack(side="left", padx=3)
        T.style_button(b, bg=_c(bg_n), hover_bg=_c(hov_n))

    # ── MASTER CONTROLS ───────────────────────────────────────
    mc = tk.Frame(root, bg=_c("CARD"),
                  highlightbackground=_c("BORDER"), highlightthickness=1)
    mc.pack(fill="x", padx=20, pady=(16, 8))
    mci = tk.Frame(mc, bg=_c("CARD")); mci.pack(fill="x", padx=16, pady=12)

    mch = tk.Frame(mci, bg=_c("CARD")); mch.pack(fill="x", pady=(0, 10))
    tk.Label(mch, text="Master Controls", bg=_c("CARD"), fg=_c("TXT"),
             font=_c("FONT_HEADING")).pack(side="left")

    mon = [config.get("monitor_enabled", True)]
    def _mon_lbl(): return "Hear Myself: ON" if mon[0] else "Sounds Only"
    def _mon_bg():  return _c("SUCCESS") if mon[0] else _c("BTN")
    def _mon_fg():  return "white"       if mon[0] else _c("TXT")

    mon_btn = tk.Button(mch, text=_mon_lbl(), bg=_mon_bg(), fg=_mon_fg(),
                        font=_c("FONT_SMALL"), padx=12, pady=5)
    mon_btn.pack(side="right")

    def _toggle_mon():
        mon[0] = not mon[0]
        config["monitor_enabled"] = mon[0]
        save_config(config)
        if _ae: _ae.set_monitor_enabled(mon[0])
        mon_btn.config(text=_mon_lbl(), bg=_mon_bg(), fg=_mon_fg())
        T.style_button(mon_btn, bg=_mon_bg(),
                       hover_bg=_c("SUCCESS_GLOW") if mon[0] else _c("BTN_HOVER"))

    mon_btn.config(command=_toggle_mon)
    T.style_button(mon_btn, bg=_mon_bg(),
                   hover_bg=_c("SUCCESS_GLOW") if mon[0] else _c("BTN_HOVER"))

    vf = tk.Frame(mci, bg=_c("CARD")); vf.pack(fill="x")

    def _slider(parent, label, key):
        f = tk.Frame(parent, bg=_c("CARD"))
        f.pack(side="left", fill="x", expand=True, padx=(0, 12))
        lf = tk.Frame(f, bg=_c("CARD")); lf.pack(fill="x", pady=(0, 4))
        tk.Label(lf, text=label, bg=_c("CARD"), fg=_c("SUBTXT"),
                 font=_c("FONT_SMALL")).pack(side="left")
        vl = tk.Label(lf, text=f"{int(config.get(key,1.0)*100)}%",
                      bg=_c("CARD"), fg=_c("ACCENT"), font=_c("FONT_MONO"))
        vl.pack(side="right")
        sl = tk.Scale(f, from_=0, to=2, resolution=0.01, orient="horizontal",
                      bg=_c("CARD"), fg=_c("TXT"), troughcolor=_c("BTN"),
                      highlightthickness=0, showvalue=0)
        sl.set(config.get(key, 1.0))
        def _cmd(v, k=key, lbl=vl):
            config[k] = float(v); lbl.config(text=f"{int(float(v)*100)}%")
            save_config(config)
        sl.config(command=_cmd); sl.pack(fill="x")

    _slider(vf, "Microphone",  "mic_volume")
    _slider(vf, "Headphones",  "headphone_volume")

    # ── SOUNDS HEADER ─────────────────────────────────────────
    sh = tk.Frame(root, bg=_c("BG")); sh.pack(fill="x", padx=20, pady=(8, 4))
    tk.Label(sh, text="Sounds", bg=_c("BG"), fg=_c("TXT"),
             font=_c("FONT_HEADING")).pack(side="left")
    count_lbl = tk.Label(sh, text="", bg=_c("BG"), fg=_c("SUBTXT"),
                         font=_c("FONT_SMALL"))
    count_lbl.pack(side="left", padx=(10, 0))

    # ── SCROLL CANVAS ─────────────────────────────────────────
    wrap = tk.Frame(root, bg=_c("BG"))
    wrap.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    scrollbar = tk.Scrollbar(wrap, orient="vertical")
    canvas    = tk.Canvas(wrap, bg=_c("BG"), highlightthickness=0,
                          yscrollcommand=scrollbar.set)
    scrollbar.config(command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    content = tk.Frame(canvas, bg=_c("BG"))
    win_id  = canvas.create_window((0, 0), window=content, anchor="nw")
    canvas.bind("<Configure>", lambda e: canvas.itemconfig(win_id, width=e.width))
    content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def _scroll(e):  canvas.yview_scroll(int(-1*(e.delta/120)), "units")
    def _scu(e):     canvas.yview_scroll(-1, "units")
    def _scd(e):     canvas.yview_scroll( 1, "units")
    for w in (canvas, root, wrap):
        w.bind("<MouseWheel>", _scroll, add="+")
        w.bind("<Button-4>",   _scu,    add="+")
        w.bind("<Button-5>",   _scd,    add="+")

    _setup_drag_drop(canvas)

    play_btns   = {}
    badge_rows  = {}   # name → frame holding effect badges

    # ─────────────────────────────────────────────────────────
    # BADGE ROW  –  shows active effects as coloured pills
    # ─────────────────────────────────────────────────────────
    def _rebuild_badges(name):
        if name not in badge_rows: return
        row = badge_rows[name]
        for w in row.winfo_children(): w.destroy()
        cur = _sm.sounds if _sm else sounds
        if name not in cur: return
        active = get_active_effects(cur[name])
        if not active:
            tk.Label(row, text="No effects active", bg=_c("CARD"),
                     fg=_c("SUBTXT_DARK"), font=_c("FONT_SMALL")).pack(side="left")
        else:
            for k in active:
                lbl = EFFECTS.get(k, k)
                pill = tk.Label(row, text=lbl,
                                bg=_c("ACCENT_DARK"), fg=_c("TXT"),
                                font=_c("FONT_SMALL"), padx=7, pady=2)
                pill.pack(side="left", padx=(0, 4))

    # ─────────────────────────────────────────────────────────
    # REFRESH
    # ─────────────────────────────────────────────────────────
    def refresh():
        for w in content.winfo_children(): w.destroy()
        play_btns.clear(); badge_rows.clear()
        cur = _sm.sounds if _sm else sounds
        count_lbl.config(text=f"{len(cur)} loaded")

        if not cur:
            ef = tk.Frame(content, bg=_c("BG")); ef.pack(pady=80)
            tk.Label(ef, text="No sounds yet",
                     bg=_c("BG"), fg=_c("SUBTXT"), font=("Segoe UI", 14)).pack()
            tk.Label(ef, text="Drag & drop audio files here, or click  +  Add Sound",
                     bg=_c("BG"), fg=_c("SUBTXT_DARK"), font=_c("FONT_MAIN")).pack(pady=(6,0))
            for w in (ef, *ef.winfo_children()):
                w.bind("<MouseWheel>", _scroll, add="+")
            return

        for name, s in cur.items():
            init_sound_effects(s)
            playing = s.get("playing", False)

            card = tk.Frame(content, bg=_c("CARD"),
                            highlightbackground=_c("BORDER"), highlightthickness=1)
            card.pack(fill="x", pady=(0, 10))
            ci = tk.Frame(card, bg=_c("CARD")); ci.pack(fill="both", padx=16, pady=12)

            # Row 1: play / effects popup / editor / delete
            r1 = tk.Frame(ci, bg=_c("CARD")); r1.pack(fill="x", pady=(0, 8))

            pb = tk.Button(r1,
                           text=f"▶  {name}" if playing else name,
                           bg=_c("SUCCESS_GLOW") if playing else _c("BTN"),
                           fg="#fff" if playing else _c("TXT"),
                           font=_c("FONT_LARGE"), anchor="w",
                           padx=20, pady=11,
                           command=lambda n=name: (_sm.toggle_sound(n), refresh()))
            pb.pack(side="left", fill="x", expand=True, padx=(0, 6))
            T.style_button(pb,
                           bg=_c("SUCCESS_GLOW") if playing else _c("BTN"),
                           hover_bg=_c("SUCCESS") if playing else _c("BTN_HOVER"))
            play_btns[name] = pb

            # Editor button
            ed_btn = tk.Button(r1, text="✎", bg=_c("BTN"), fg=_c("TXT"),
                               font=("Segoe UI", 13), width=3, pady=11)
            ed_btn.pack(side="right", padx=(4, 0))
            ed_btn.config(command=lambda n=name: _open_editor(n))
            T.style_button(ed_btn)

            # Effects popup button
            fx_btn = tk.Button(r1, text="✨", bg=_c("BTN"), fg=_c("TXT"),
                               font=("Segoe UI", 13), width=3, pady=11)
            fx_btn.pack(side="right", padx=(4, 0))
            fx_btn.config(command=lambda n=name, b=fx_btn: _effect_popup(n, b, _rebuild_badges))
            T.style_button(fx_btn)

            # Delete
            db = tk.Button(r1, text="×", bg=_c("DANGER_DARK"), fg="white",
                           font=("Segoe UI", 14, "bold"), width=3, pady=11,
                           command=lambda n=name: (_sm.remove_sound(n), refresh()))
            db.pack(side="right")
            T.style_button(db, bg=_c("DANGER_DARK"), hover_bg=_c("DANGER"))

            # Row 2: effect badges
            r2 = tk.Frame(ci, bg=_c("CARD")); r2.pack(fill="x", pady=(0, 8))
            tk.Label(r2, text="Effects: ", bg=_c("CARD"), fg=_c("SUBTXT"),
                     font=_c("FONT_SMALL")).pack(side="left")
            badge_row = tk.Frame(r2, bg=_c("CARD")); badge_row.pack(side="left", fill="x")
            badge_rows[name] = badge_row
            _rebuild_badges(name)

            # Row 3: hotkey
            r3 = tk.Frame(ci, bg=_c("CARD")); r3.pack(fill="x", pady=(0, 8))
            tk.Label(r3, text="Hotkey:", bg=_c("CARD"), fg=_c("SUBTXT"),
                     font=_c("FONT_SMALL")).pack(side="left")
            hk = s.get("hotkey")
            tk.Label(r3, text=hk or "Not set",
                     bg=_c("BTN"), fg=_c("ACCENT") if hk else _c("SUBTXT"),
                     font=_c("FONT_MONO"), padx=8, pady=3).pack(side="left", padx=(8, 6))
            hkb = tk.Button(r3, text=f"⌨  {'Change' if hk else 'Set'}",
                            bg=_c("BTN"), fg=_c("TXT"), font=_c("FONT_SMALL"),
                            padx=8, pady=3,
                            command=lambda n=name: _hotkey_dialog(n, refresh))
            hkb.pack(side="left", padx=(0,4)); T.style_button(hkb)
            if hk:
                clr = tk.Button(r3, text="✕", bg=_c("DANGER_DARK"), fg="white",
                                font=_c("FONT_SMALL"), padx=6, pady=3,
                                command=lambda n=name: (_sm.remove_hotkey(n), refresh()))
                clr.pack(side="left")
                T.style_button(clr, bg=_c("DANGER_DARK"), hover_bg=_c("DANGER"))

            # Row 4: volume
            r4 = tk.Frame(ci, bg=_c("CARD")); r4.pack(fill="x")
            r4h = tk.Frame(r4, bg=_c("CARD")); r4h.pack(fill="x", pady=(0,4))
            tk.Label(r4h, text="Volume", bg=_c("CARD"), fg=_c("SUBTXT"),
                     font=_c("FONT_SMALL")).pack(side="left")
            vl = tk.Label(r4h, text=f"{int(s['volume']*100)}%",
                          bg=_c("CARD"), fg=_c("ACCENT"), font=_c("FONT_MONO"))
            vl.pack(side="right")
            sl = tk.Scale(r4, from_=0, to=2, resolution=0.01, orient="horizontal",
                          bg=_c("CARD"), fg=_c("TXT"), troughcolor=_c("BTN"),
                          highlightthickness=0, showvalue=0)
            sl.set(s["volume"])
            def _sv(v, n=name, lbl=vl):
                _sm.set_sound_volume(n, float(v))
                lbl.config(text=f"{int(float(v)*100)}%")
            sl.config(command=_sv); sl.pack(fill="x")

            # Bind scroll to all card children
            for widget in (card, ci, r1, r2, r3, r4, r4h, pb, fx_btn, ed_btn,
                           db, hkb, sl, badge_row, vl):
                widget.bind("<MouseWheel>", _scroll, add="+")
                widget.bind("<Button-4>",   _scu,    add="+")
                widget.bind("<Button-5>",   _scd,    add="+")

        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    # Live play-state update
    def _live():
        if not root.winfo_exists(): return
        cur = _sm.sounds if _sm else sounds
        for n, b in play_btns.items():
            if n not in cur: continue
            p = cur[n].get("playing", False)
            want_bg  = _c("SUCCESS_GLOW") if p else _c("BTN")
            want_txt = f"▶  {n}" if p else n
            want_fg  = "#fff" if p else _c("TXT")
            if b["bg"] != want_bg:
                b.config(bg=want_bg, text=want_txt, fg=want_fg)
        root.after(100, _live)

    def _open_editor(name):
        from ui.sound_editor import open_editor
        cur = _sm.sounds if _sm else sounds
        open_editor(root, name, cur, on_close=lambda: (
            refresh(),
            _rebuild_badges(name)
        ))

    _current_refresh = refresh
    refresh()
    _live()

    if not config.get("mic_out"):
        root.after(600, lambda: (
            messagebox.showinfo("Welcome to Soundboard Pro",
                                "Please open Settings to configure your audio devices."),
            _open_settings()
        ))


# ─────────────────────────────────────────────────────────────
# STARTUP
# ─────────────────────────────────────────────────────────────
try:
    config = load_config()
    T.set_theme(config.get("theme", "dark"))

    root = tk.Tk()
    root.title(f"Soundboard Pro  v{__version__}")
    root.geometry("760x900")
    root.configure(bg=_c("BG"))
    root.minsize(600, 500)

    # Show splash immediately, load heavy stuff right after
    lf = tk.Frame(root, bg=_c("BG")); lf.pack(expand=True, fill="both")
    tk.Label(lf, text="SOUNDBOARD PRO", bg=_c("BG"), fg=_c("ACCENT"),
             font=("Segoe UI", 26, "bold")).pack(pady=(260, 10))
    status = tk.Label(lf, text="Loading…", bg=_c("BG"), fg=_c("SUBTXT"),
                      font=_c("FONT_MAIN"))
    status.pack()
    root.update()

    def _startup():
        try:
            status.config(text="Loading audio libraries…"); root.update()
            _load_modules()
            status.config(text="Initialising audio…");     root.update()
            _init_audio()
            status.config(text="Building interface…");      root.update()
            build_main_app()
            try:
                from updater import check_updates_in_background
                check_updates_in_background(root)
            except Exception: pass
        except Exception:
            traceback.print_exc()
            messagebox.showerror("Startup Error",
                                 "Soundboard Pro failed to start.\nSee console for details.")

    root.after(80, _startup)

    def _on_close():
        save_config(config)
        try:
            import keyboard; keyboard.unhook_all()
        except Exception: pass
        if _ae:
            try: _ae.stop()
            except Exception: pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", _on_close)
    root.mainloop()

except Exception:
    traceback.print_exc()
    try:
        _r = tk.Tk(); _r.withdraw()
        messagebox.showerror("Fatal Error",
                             "Soundboard Pro could not start.\nCheck the console.")
        _r.destroy()
    except Exception: pass
