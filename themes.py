# themes.py - Theme system for Soundboard Pro

THEMES = {
    'dark': {
        'name': 'Dark Mode',
        'BG': '#0d1117',
        'PANEL': '#161b22',
        'CARD': '#1c2128',
        'BTN': '#21262d',
        'BTN_HOVER': '#30363d',
        'BORDER': '#30363d',
        'TXT': '#e6edf3',
        'SUBTXT': '#8d96a0',
        'SUBTXT_DARK': '#6e7681',
        'ACCENT': '#58a6ff',
        'ACCENT_DARK': '#1f6feb',
        'SUCCESS': '#3fb950',
        'SUCCESS_GLOW': '#2ea043',
        'DANGER': '#f85149',
        'DANGER_DARK': '#da3633',
    },
    'light': {
        'name': 'Light Mode',
        'BG': '#ffffff',
        'PANEL': '#f6f8fa',
        'CARD': '#ffffff',
        'BTN': '#e1e4e8',
        'BTN_HOVER': '#d0d7de',
        'BORDER': '#d0d7de',
        'TXT': '#24292f',
        'SUBTXT': '#57606a',
        'SUBTXT_DARK': '#6e7781',
        'ACCENT': '#0969da',
        'ACCENT_DARK': '#0550ae',
        'SUCCESS': '#1a7f37',
        'SUCCESS_GLOW': '#116329',
        'DANGER': '#cf222e',
        'DANGER_DARK': '#a40e26',
    },
    'purple': {
        'name': 'Purple Dream',
        'BG': '#1a0033',
        'PANEL': '#2d0052',
        'CARD': '#3d0066',
        'BTN': '#4d0080',
        'BTN_HOVER': '#5e0099',
        'BORDER': '#6b00b3',
        'TXT': '#ffffff',
        'SUBTXT': '#c4b5fd',
        'SUBTXT_DARK': '#a78bfa',
        'ACCENT': '#a855f7',
        'ACCENT_DARK': '#9333ea',
        'SUCCESS': '#10b981',
        'SUCCESS_GLOW': '#059669',
        'DANGER': '#f43f5e',
        'DANGER_DARK': '#e11d48',
    }
}

# Current theme
current_theme = 'dark'

# Export current theme colors as module-level variables
def _apply_theme(theme_name):
    """Apply theme colors to module globals"""
    global current_theme
    current_theme = theme_name
    theme = THEMES.get(theme_name, THEMES['dark'])
    
    globals().update(theme)

# Initialize with dark theme
_apply_theme('dark')

def set_theme(theme_name):
    """
    Change the active theme
    
    Args:
        theme_name: Name of theme ('dark', 'light', 'purple')
    """
    if theme_name in THEMES:
        _apply_theme(theme_name)
        return True
    return False

def get_theme():
    """Get current theme name"""
    return current_theme

def get_theme_names():
    """Get list of available theme names"""
    return list(THEMES.keys())

# Font definitions
FONT_MAIN = ("Segoe UI", 10)
FONT_SMALL = ("Segoe UI", 9)
FONT_LARGE = ("Segoe UI", 12, "bold")
FONT_HEADING = ("Segoe UI", 11, "bold")
FONT_BUTTON = ("Segoe UI", 10, "bold")
FONT_MONO = ("Consolas", 9)

# Icons (Unicode)
ICON_SETTINGS = "⚙"
ICON_ADD = "+"
ICON_STOP = "■"
ICON_DELETE = "×"
ICON_KEYBOARD = "⌨"
ICON_CLEAR = "×"
ICON_PLAY = "▶"
ICON_EDIT = "✎"
ICON_EFFECTS = "✨"

# Button styling helper
def style_button(btn, bg=None, hover_bg=None, active_bg=None):
    """
    Add hover effects to a button
    
    Args:
        btn: Tkinter button widget
        bg: Normal background color
        hover_bg: Hover background color
        active_bg: Active/pressed background color
    """
    if bg is None:
        bg = btn['bg']
    if hover_bg is None:
        hover_bg = globals().get('BTN_HOVER', '#30363d')
    if active_bg is None:
        active_bg = bg
    
    def on_enter(e):
        btn['bg'] = hover_bg
    
    def on_leave(e):
        btn['bg'] = bg
    
    def on_press(e):
        btn['bg'] = active_bg
    
    def on_release(e):
        btn['bg'] = hover_bg if btn.winfo_containing(e.x_root, e.y_root) == btn else bg
    
    btn.bind('<Enter>', on_enter)
    btn.bind('<Leave>', on_leave)
    btn.bind('<Button-1>', on_press)
    btn.bind('<ButtonRelease-1>', on_release)