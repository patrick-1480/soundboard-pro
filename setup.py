from setuptools import setup

APP = ['app.py']
DATA_FILES = [
    ('ui', ['ui/__init__.py', 'ui/settings.py', 'ui/theme.py', 'ui/sound_card.py']),
    ('', ['config.json']),  # Add config.json
]

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': 'Soundboard Pro',
        'CFBundleDisplayName': 'Soundboard Pro',
        'CFBundleGetInfoString': 'Professional Audio Soundboard',
        'CFBundleIdentifier': 'com.patricksoundboard.soundboardpro',
        'CFBundleVersion': '2.1.2',
        'CFBundleShortVersionString': '2.1.2',
        'NSHumanReadableCopyright': '© 2025 Patrick',
        'NSMicrophoneUsageDescription': 'Soundboard Pro needs microphone access for audio processing.',
        'LSMinimumSystemVersion': '10.15',
    },
    'packages': ['sounddevice', 'numpy', 'librosa', 'keyboard', 'scipy', 'numba', 'cffi', 'soundfile'],
    'includes': ['tkinter', 'tkinter.messagebox', 'tkinter.filedialog'],  # Add these
    'frameworks': [],  # Add frameworks if needed
    'resources': [],
}

setup(
    name='Soundboard Pro',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)