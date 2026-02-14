# ui/sound_editor.py
# Sound editor: waveform, draggable trim handles, effect toggles.
# Rules obeyed to prevent crashes:
#   - NO stipple= anywhere (crashes Windows Tk)
#   - NO mixing grid and pack in the same container
#   - All layouts use pack only
#   - All exceptions caught and printed

import tkinter as tk
from tkinter import messagebox
import numpy as np
import themes as T

from effects import (
    EFFECTS, init_sound_effects, toggle_effect,
    set_effect_param, trim_sound, reset_trim,
)

def _get_sr():
    """Get the current stream SR from sound_manager (set at runtime)."""
    try:
        import sound_manager as _sm
        return _sm.TARGET_SR
    except Exception:
        return 48000


def _c(n):
    return getattr(T, n)


# ─────────────────────────────────────────────────────────────
# WAVEFORM CANVAS
# ─────────────────────────────────────────────────────────────
class WaveformCanvas(tk.Canvas):
    """Waveform display with draggable trim handles. No stipple used."""

    HANDLE_W = 10   # half-width of grab zone around each handle

    def __init__(self, parent, sound, **kw):
        kw.setdefault("bg", _c("BG"))
        kw.setdefault("highlightthickness", 1)
        kw.setdefault("highlightbackground", _c("BORDER"))
        kw.setdefault("height", 140)
        super().__init__(parent, **kw)

        self._sound = sound
        self._drag  = None  # "left" or "right"

        total = max(len(sound.get("original_data", sound["data"])) / _get_sr(), 0.001)
        self._total      = total
        self._trim_start = 0.0
        self._trim_end   = total

        self.bind("<Configure>",       self._draw)
        self.bind("<ButtonPress-1>",   self._press)
        self.bind("<B1-Motion>",       self._motion)
        self.bind("<ButtonRelease-1>", self._release)

    # ── coordinate helpers ───────────────────────────────────
    def _sec_to_x(self, sec):
        w = self.winfo_width()
        if w < 2 or self._total <= 0:
            return 0
        return int((sec / self._total) * w)

    def _x_to_sec(self, x):
        w = self.winfo_width()
        if w < 2:
            return 0.0
        return max(0.0, min(self._total, (x / w) * self._total))

    # ── drawing ──────────────────────────────────────────────
    def _draw(self, _event=None):
        try:
            self.delete("all")
            w = self.winfo_width()
            h = self.winfo_height()
            if w < 4 or h < 4:
                return

            data = self._sound.get("original_data", self._sound["data"])
            samples = len(data)
            mid = h // 2
            amp = mid * 0.88

            # Waveform bars
            for px in range(w):
                i0 = int(px * samples / w)
                i1 = min(samples, i0 + max(1, samples // w))
                chunk = data[i0:i1]
                peak = float(np.max(np.abs(chunk))) if len(chunk) else 0.0
                yt = mid - int(peak * amp)
                yb = mid + int(peak * amp)
                self.create_line(px, yt, px, yb, fill=_c("ACCENT"), width=1)

            lx = self._sec_to_x(self._trim_start)
            rx = self._sec_to_x(self._trim_end)

            # Dimmed regions outside the trim selection – solid dark overlay
            dim = _c("PANEL")
            if lx > 0:
                self.create_rectangle(0, 0, lx, h, fill=dim, outline="")
            if rx < w:
                self.create_rectangle(rx, 0, w, h, fill=dim, outline="")

            # Centre-line
            self.create_line(0, mid, w, mid, fill=_c("BORDER"), dash=(2, 4))

            # Trim handle lines
            self.create_line(lx, 0, lx, h, fill=_c("SUCCESS"), width=2)
            self.create_line(rx, 0, rx, h, fill=_c("DANGER"),  width=2)

            # Handle grip rectangles (top)
            hw = self.HANDLE_W
            self.create_rectangle(lx - hw, 0, lx + hw, 20,
                                  fill=_c("SUCCESS"), outline="")
            self.create_rectangle(rx - hw, 0, rx + hw, 20,
                                  fill=_c("DANGER"),  outline="")

            # Time labels
            self.create_text(lx + hw + 2, 10, anchor="w",
                             text=f"{self._trim_start:.2f}s",
                             fill=_c("TXT"), font=_c("FONT_MONO"))
            self.create_text(rx - hw - 2, 10, anchor="e",
                             text=f"{self._trim_end:.2f}s",
                             fill=_c("TXT"), font=_c("FONT_MONO"))

        except Exception as e:
            print(f"[waveform] draw error: {e}")

    # ── drag logic ───────────────────────────────────────────
    def _press(self, e):
        lx = self._sec_to_x(self._trim_start)
        rx = self._sec_to_x(self._trim_end)
        hw = self.HANDLE_W + 4
        if abs(e.x - lx) <= hw:
            self._drag = "left"
        elif abs(e.x - rx) <= hw:
            self._drag = "right"
        else:
            self._drag = None

    def _motion(self, e):
        if not self._drag:
            return
        sec = self._x_to_sec(e.x)
        if self._drag == "left":
            self._trim_start = min(sec, self._trim_end - 0.05)
        else:
            self._trim_end = max(sec, self._trim_start + 0.05)
        self._draw()

    def _release(self, e):
        self._drag = None

    def reset_handles(self):
        total = max(len(self._sound.get("original_data", self._sound["data"])) / _get_sr(), 0.001)
        self._total      = total
        self._trim_start = 0.0
        self._trim_end   = total
        self._draw()

    def get_trim(self):
        return self._trim_start, self._trim_end


# ─────────────────────────────────────────────────────────────
# EDITOR WINDOW
# ─────────────────────────────────────────────────────────────
def open_editor(parent, sound_name: str, sounds: dict, on_close=None):
    try:
        if sound_name not in sounds:
            messagebox.showerror("Editor", f"Sound '{sound_name}' not found.")
            return

        sound = sounds[sound_name]
        init_sound_effects(sound)

        # Keep an untouched backup for full reset
        if "_editor_backup" not in sound:
            sound["_editor_backup"] = sound["original_data"].copy()

        win = tk.Toplevel(parent)
        win.title(f"Sound Editor  –  {sound_name}")
        win.geometry("820x660")
        win.configure(bg=_c("BG"))
        win.resizable(True, True)
        win.minsize(640, 500)

        # ── HEADER ───────────────────────────────────────────
        hdr = tk.Frame(win, bg=_c("PANEL"), height=52)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text=f"  ✎  {sound_name}",
                 bg=_c("PANEL"), fg=_c("TXT"),
                 font=("Segoe UI", 13, "bold")).pack(side="left", pady=14)
        dur_lbl = tk.Label(hdr, text="",
                           bg=_c("PANEL"), fg=_c("SUBTXT"), font=_c("FONT_SMALL"))
        dur_lbl.pack(side="left", padx=8)

        def _update_dur():
            secs = len(sound["data"]) / _get_sr()
            orig = len(sound["original_data"]) / _get_sr()
            dur_lbl.config(text=f"{secs:.2f}s  (original: {orig:.2f}s)")

        _update_dur()

        # ── MAIN AREA  (two columns via two side-by-side frames, using pack)
        main = tk.Frame(win, bg=_c("BG"))
        main.pack(fill="both", expand=True, padx=14, pady=10)

        left  = tk.Frame(main, bg=_c("BG"))
        right = tk.Frame(main, bg=_c("BG"), width=240)

        # Pack right first so it stays fixed width; left takes remaining space
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)
        left.pack(side="left", fill="both", expand=True)

        # ── LEFT: waveform ────────────────────────────────────
        tk.Label(left, text="Waveform & Trim",
                 bg=_c("BG"), fg=_c("TXT"),
                 font=_c("FONT_HEADING")).pack(anchor="w", pady=(0, 4))
        tk.Label(left,
                 text="Drag the green handle (start) or red handle (end) to set trim points",
                 bg=_c("BG"), fg=_c("SUBTXT"), font=_c("FONT_SMALL")).pack(anchor="w", pady=(0, 8))

        wf = WaveformCanvas(left, sound)
        wf.pack(fill="x", ipady=0)

        # Trim buttons
        tbf = tk.Frame(left, bg=_c("BG")); tbf.pack(fill="x", pady=8)

        def _apply_trim():
            s, e = wf.get_trim()
            if e - s < 0.05:
                messagebox.showwarning("Trim", "Selection is too short (min 0.05s).",
                                       parent=win)
                return
            trim_sound(sound, s, e)
            wf.reset_handles()
            _update_dur()

        def _reset_trim():
            if "_editor_backup" in sound:
                reset_trim(sound, sound["_editor_backup"])
                wf.reset_handles()
                _update_dur()

        for txt, cmd, bg_n, hov_n in [
            ("✂  Apply Trim",        _apply_trim,  "ACCENT", "BTN_HOVER"),
            ("↺  Reset to Original", _reset_trim,  "BTN",    "BTN_HOVER"),
        ]:
            b = tk.Button(tbf, text=txt, bg=_c(bg_n), fg=_c("TXT"),
                          font=_c("FONT_BUTTON"), command=cmd, padx=12, pady=7)
            b.pack(side="left", padx=(0, 8))
            T.style_button(b, bg=_c(bg_n), hover_bg=_c(hov_n))

        # Effect param sliders
        params_card = tk.Frame(left, bg=_c("CARD"),
                               highlightbackground=_c("BORDER"), highlightthickness=1)
        params_card.pack(fill="x", pady=(4, 0))
        pci = tk.Frame(params_card, bg=_c("CARD"))
        pci.pack(fill="x", padx=12, pady=10)

        tk.Label(pci, text="Effect Parameters",
                 bg=_c("CARD"), fg=_c("TXT"), font=_c("FONT_HEADING")).pack(anchor="w", pady=(0, 8))

        def _param_slider(label, param, lo, hi, default):
            f  = tk.Frame(pci, bg=_c("CARD")); f.pack(fill="x", pady=(0, 6))
            lf = tk.Frame(f,   bg=_c("CARD")); lf.pack(fill="x")
            tk.Label(lf, text=label, bg=_c("CARD"), fg=_c("SUBTXT"),
                     font=_c("FONT_SMALL")).pack(side="left")
            current = sound["effect_params"].get(param, default)
            vl = tk.Label(lf, text=f"{current:.2f}",
                          bg=_c("CARD"), fg=_c("ACCENT"), font=_c("FONT_MONO"))
            vl.pack(side="right")
            sl = tk.Scale(f, from_=lo, to=hi, resolution=0.01, orient="horizontal",
                          bg=_c("CARD"), fg=_c("TXT"), troughcolor=_c("BTN"),
                          highlightthickness=0, showvalue=0)
            sl.set(current)
            def _cmd(v, p=param, lbl=vl):
                set_effect_param(sound, p, float(v))
                lbl.config(text=f"{float(v):.2f}")
            sl.config(command=_cmd)
            sl.pack(fill="x")

        _param_slider("Echo Delay (s)",   "echo_delay",    0.05, 1.5,  0.30)
        _param_slider("Echo Decay",        "echo_decay",    0.0,  1.0,  0.50)
        _param_slider("Fade Duration (s)", "fade_duration", 0.05, 5.0,  0.50)

        # ── RIGHT: effect toggles ─────────────────────────────
        tk.Label(right, text="Effects",
                 bg=_c("BG"), fg=_c("TXT"), font=_c("FONT_HEADING")).pack(anchor="w", pady=(0, 4))
        tk.Label(right, text="Toggle on / off\nNo audio restart",
                 bg=_c("BG"), fg=_c("SUBTXT"), font=_c("FONT_SMALL"),
                 justify="left").pack(anchor="w", pady=(0, 10))

        fx_btns = {}

        def _make_fx_btn(key, label):
            active = sound["effects"].get(key, False)
            b = tk.Button(right,
                          text=f"✓  {label}" if active else f"○  {label}",
                          bg=_c("SUCCESS_GLOW") if active else _c("BTN"),
                          fg="white"            if active else _c("TXT"),
                          font=_c("FONT_BUTTON"), anchor="w",
                          padx=10, pady=9)
            b.pack(fill="x", pady=(0, 5))

            def _toggle(k=key, btn=b, lbl=label):
                new_on = toggle_effect(sound, k)
                btn.config(
                    text=f"✓  {lbl}" if new_on else f"○  {lbl}",
                    bg=_c("SUCCESS_GLOW") if new_on else _c("BTN"),
                    fg="white"            if new_on else _c("TXT"),
                )
                T.style_button(btn,
                               bg=_c("SUCCESS_GLOW") if new_on else _c("BTN"),
                               hover_bg=_c("SUCCESS") if new_on else _c("BTN_HOVER"))
                _update_dur()

            b.config(command=_toggle)
            T.style_button(b,
                           bg=_c("SUCCESS_GLOW") if active else _c("BTN"),
                           hover_bg=_c("SUCCESS") if active else _c("BTN_HOVER"))
            fx_btns[key] = b

        for k, lbl in EFFECTS.items():
            _make_fx_btn(k, lbl)

        # ── BOTTOM BAR ────────────────────────────────────────
        bot = tk.Frame(win, bg=_c("PANEL"), height=52)
        bot.pack(fill="x", side="bottom"); bot.pack_propagate(False)
        bi = tk.Frame(bot, bg=_c("PANEL")); bi.pack(side="right", padx=14, pady=10)

        tk.Label(bi, text="Changes apply live — no audio restart needed",
                 bg=_c("PANEL"), fg=_c("SUBTXT"),
                 font=_c("FONT_SMALL")).pack(side="left", padx=(0, 16))

        def _done():
            win.destroy()
            if on_close:
                try: on_close()
                except Exception: pass

        done_b = tk.Button(bi, text="Done", bg=_c("ACCENT"), fg="white",
                           font=_c("FONT_BUTTON"), command=_done, padx=22, pady=8)
        done_b.pack(side="right")
        T.style_button(done_b, bg=_c("ACCENT"), hover_bg=_c("BTN_HOVER"))

    except Exception:
        import traceback
        traceback.print_exc()
        try:
            messagebox.showerror("Editor Error",
                                 "The sound editor encountered an error.\n"
                                 "Check the console for details.")
        except Exception:
            pass
