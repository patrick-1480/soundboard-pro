# themes.py
# Theme colours are stored in THEMES dict.
# set_theme() writes them as module-level globals.
# Never do "from themes import *" in widgets — always call _c("NAME") instead
# so widgets always pick up the current theme at draw time.

THEMES = {
    "dark": {
        "BG":           "#0d1117",
        "PANEL":        "#161b22",
        "CARD":         "#1c2128",
        "BTN":          "#21262d",
        "BTN_HOVER":    "#30363d",
        "BORDER":       "#30363d",
        "TXT":          "#e6edf3",
        "SUBTXT":       "#8d96a0",
        "SUBTXT_DARK":  "#6e7681",
        "ACCENT":       "#58a6ff",
        "ACCENT_DARK":  "#1f3a5e",
        "SUCCESS":      "#3fb950",
        "SUCCESS_GLOW": "#2ea043",
        "DANGER":       "#f85149",
        "DANGER_DARK":  "#da3633",
    },
    "light": {
        "BG":           "#f6f8fa",
        "PANEL":        "#ffffff",
        "CARD":         "#ffffff",
        "BTN":          "#e1e4e8",
        "BTN_HOVER":    "#d0d7de",
        "BORDER":       "#d0d7de",
        "TXT":          "#24292f",
        "SUBTXT":       "#57606a",
        "SUBTXT_DARK":  "#6e7781",
        "ACCENT":       "#0969da",
        "ACCENT_DARK":  "#dbeafe",
        "SUCCESS":      "#1a7f37",
        "SUCCESS_GLOW": "#116329",
        "DANGER":       "#cf222e",
        "DANGER_DARK":  "#a40e26",
    },
    "purple": {
        "BG":           "#1a0033",
        "PANEL":        "#2d0052",
        "CARD":         "#3d0066",
        "BTN":          "#4d0080",
        "BTN_HOVER":    "#5e0099",
        "BORDER":       "#7c00cc",
        "TXT":          "#f0e6ff",
        "SUBTXT":       "#c4b5fd",
        "SUBTXT_DARK":  "#a78bfa",
        "ACCENT":       "#c084fc",
        "ACCENT_DARK":  "#4a0080",
        "SUCCESS":      "#10b981",
        "SUCCESS_GLOW": "#059669",
        "DANGER":       "#f43f5e",
        "DANGER_DARK":  "#e11d48",
    },
}

# Fonts (not theme-dependent)
FONT_MAIN    = ("Segoe UI", 10)
FONT_SMALL   = ("Segoe UI", 9)
FONT_LARGE   = ("Segoe UI", 12, "bold")
FONT_HEADING = ("Segoe UI", 11, "bold")
FONT_BUTTON  = ("Segoe UI", 10, "bold")
FONT_BOLD    = ("Segoe UI", 10, "bold")
FONT_MONO    = ("Consolas", 9)

_current = "dark"


def set_theme(name: str):
    global _current
    if name not in THEMES:
        name = "dark"
    _current = name
    globals().update(THEMES[name])   # write BG, PANEL, ... into module globals


def get_theme() -> str:
    return _current


# Initialise with dark theme
set_theme("dark")


def style_button(btn, bg=None, hover_bg=None, active_bg=None):
    """Attach hover/leave colour effects to a tk.Button."""
    if bg       is None: bg       = btn["bg"]
    if hover_bg is None: hover_bg = globals().get("BTN_HOVER", "#30363d")
    if active_bg is None: active_bg = bg

    btn.bind("<Enter>",          lambda e: btn.config(bg=hover_bg))
    btn.bind("<Leave>",          lambda e: btn.config(bg=bg))
    btn.bind("<Button-1>",       lambda e: btn.config(bg=active_bg))
    btn.bind("<ButtonRelease-1>",lambda e: btn.config(
        bg=hover_bg if btn.winfo_containing(e.x_root, e.y_root) is btn else bg))
