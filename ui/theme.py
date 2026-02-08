# ui/theme.py - Modern Sleek Design

import tkinter as tk

# Dark theme with modern accents
BG = "#0d1117"           # Deep dark background
PANEL = "#161b22"        # Slightly lighter panels
CARD = "#1c2128"         # Card background
BTN = "#21262d"          # Button default
BTN_HOVER = "#30363d"    # Button hover
BTN_ACTIVE = "#161b22"   # Button pressed

# Text colors
TXT = "#e6edf3"          # Primary text (bright white)
TEXT = "#e6edf3"         # Alias
SUBTXT = "#7d8590"       # Secondary text (gray)
SUBTXT_DARK = "#484f58"  # Tertiary text (darker gray)

# Accent colors (modern gradient-friendly)
ACCENT = "#58a6ff"       # Bright blue
ACCENT_DARK = "#1f6feb"  # Darker blue
SUCCESS = "#3fb950"      # Modern green
SUCCESS_GLOW = "#2ea043" # Darker green for glow effect
WARNING = "#d29922"      # Orange
DANGER = "#f85149"       # Modern red
DANGER_DARK = "#da3633"  # Darker red

# Special effects
GLOW = "#58a6ff40"       # Transparent blue glow
BORDER = "#30363d"       # Subtle borders
SEPARATOR = "#21262d"    # Divider lines

# Fonts - Modern, clean typography
FONT_MAIN = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI Semibold", 10)
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_HEADING = ("Segoe UI", 12, "bold")
FONT_BUTTON = ("Segoe UI Semibold", 10)
FONT_MONO = ("Consolas", 9)
FONT_SMALL = ("Segoe UI", 8)
FONT_LARGE = ("Segoe UI", 11)

# Icon replacements (using Unicode symbols instead of emoji)
ICON_SETTINGS = "⚙"
ICON_ADD = "+"
ICON_STOP = "■"
ICON_DELETE = "×"
ICON_PLAY = "▶"
ICON_MIC = "🎤"
ICON_HEADPHONE = "🎧"
ICON_KEYBOARD = "⌨"
ICON_CLEAR = "×"
ICON_CHECK = "✓"

# Button styling helper
def style_button(button, bg=BTN, fg=TXT, hover_bg=BTN_HOVER, active_bg=BTN_ACTIVE):
    """Apply modern button styling with hover effects"""
    button.config(
        bg=bg,
        fg=fg,
        relief="flat",
        borderwidth=0,
        padx=12,
        pady=8,
        font=FONT_BUTTON,
        cursor="hand2"
    )
    
    # Hover effects
    def on_enter(e):
        button['background'] = hover_bg
    
    def on_leave(e):
        button['background'] = bg
    
    def on_press(e):
        button['background'] = active_bg
    
    def on_release(e):
        button['background'] = hover_bg
    
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)
    button.bind("<Button-1>", on_press)
    button.bind("<ButtonRelease-1>", on_release)