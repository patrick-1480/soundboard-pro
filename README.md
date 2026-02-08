# 🎵 Soundboard Pro - Enhanced Edition

A professional Python soundboard with **global hotkeys**, **live voice passthrough**, **dual audio output**, and more!

## ✨ Features

### Core Features
- ✅ Play multiple sounds simultaneously
- ✅ **Global hotkeys** - Works in games, Discord, anywhere!
- ✅ **Glowing buttons** - Visual feedback when sounds are playing
- ✅ **Live voice passthrough** - Talk while sounds play
- ✅ **Dual audio output** - Hear sounds in your headphones + send to mic
- ✅ Independent volume controls (mic, headphones, per-sound)
- ✅ **Auto-save settings** - All settings persist automatically!
- ✅ VB-Audio Cable integration
- ✅ Clean Discord-inspired UI

### What's New in Enhanced Edition
🆕 **Glowing Play Buttons** - Buttons turn green when sound is playing  
🆕 **Mic Passthrough** - Your voice goes through with the sounds  
🆕 **Headphone Monitor** - Hear what others hear in your headphones  
🆕 **Volume Controls** - Separate sliders for mic and headphones  
🆕 **Auto-refresh UI** - Buttons update in real-time  
🆕 **Settings Persistence** - Everything saves automatically!  

## 📦 Requirements

### Software
```bash
pip install sounddevice numpy librosa keyboard
```

Or use requirements.txt:
```bash
pip install -r requirements.txt
```

### Hardware
**VB-Audio Virtual Cable** - Download from https://vb-audio.com/Cable/
- This creates a virtual audio device to route sound
- **Alternative:** Any virtual audio cable (Voicemeeter, etc.)

## 🚀 Quick Start

### Method 1: Auto-Launch (Recommended)
Just double-click:
```
launch.bat
```
This will:
1. Check if VB Cable is installed
2. Launch the soundboard

### Method 2: Manual Launch
```bash
# Check VB Cable (optional)
python check_vb_cable.py

# Run the app
python app.py
```

## ⚙️ Setup Guide

### First Time Setup

1. **Install VB Cable** (if not already installed)
   - Download from https://vb-audio.com/Cable/
   - Run installer as administrator
   - Restart your computer

2. **Launch Soundboard**
   - Run `launch.bat` or `python app.py`
   - Click "⚙ Settings"

3. **Configure Audio Devices**
   - **Your Microphone:** Select your real microphone
   - **Virtual Mic Output:** Select "CABLE Input (VB-Audio Virtual Cable)"
   - **Headphone Output:** Select your speakers/headphones (optional)
   - Click "Apply & Restart Audio"

4. **Configure Discord/Game**
   - In Discord: Settings → Voice → Input Device → "CABLE Output"
   - In Games: Set mic input to "CABLE Output"

### Audio Flow Explained
```
Your Voice (Real Mic) ──┐
                        ├──> Mix ──> CABLE Input ──> Discord/Game hears
Soundboard Sounds ──────┘              │
                                       └──> Your Headphones (you hear)
```

## 🎮 Using the Soundboard

### Adding Sounds
1. Click "➕ Add Sound"
2. Select audio file (.wav, .mp3, .ogg, .flac)
3. Sound appears in the list!

### Setting Hotkeys
1. Click "⌨ Set" next to any sound
2. Press your desired key combo (e.g., F1, Ctrl+1, Numpad5)
3. Hotkey is registered globally!

**Hotkey Examples:**
- `f1`, `f2`, `f12` - Function keys
- `numpad1`, `numpad2` - Number pad
- `ctrl+1`, `shift+2` - With modifiers
- `ctrl+shift+f1` - Multiple modifiers

### Volume Controls

**🎤 Your Mic Volume** (0.0 - 2.0)
- Controls how loud your voice is in the mix
- Default: 1.0 (normal)
- Increase if you're too quiet

**🎧 Headphone Volume** (0.0 - 2.0)
- Controls what you hear in your headphones
- Default: 1.0 (normal)
- Set to 0 if you don't want to hear sounds

**Per-Sound Volume** (0.0 - 2.0)
- Each sound has its own slider
- 0.5 = half volume, 2.0 = double volume

### Visual Feedback
- **Gray button** = Sound ready
- **Green glowing button** = Sound currently playing
- **▶ icon** = Playing indicator

## 🎯 Pro Tips

### For Gaming
1. **Run as Administrator** - Required for hotkeys to work in most games
2. **Use Numpad** - Easy to reach while gaming (Numpad0-9)
3. **Test First** - Try hotkeys in Notepad before gaming
4. **Avoid Game Keys** - Don't use WASD, Space, etc.

### For Discord
1. **Enable Push-to-Talk** - Better control
2. **Adjust Mic Volume** - If soundboard is too loud/quiet
3. **Use Headphone Monitor** - Hear exactly what others hear

### Audio Quality
1. **Normalize Sounds** - App auto-normalizes, but you can pre-process
2. **Set Volumes** - Loud sounds to 0.5-0.8, quiet sounds to 1.5-2.0
3. **Mic Volume** - Adjust so voice and sounds blend well

### Hotkey Tips
1. **F-Keys** - F1-F12 are great for main sounds
2. **Numpad** - Perfect for quick access (Numpad1-9)
3. **Ctrl/Shift combos** - For less-used sounds
4. **Avoid conflicts** - Check other apps' hotkeys

## 🐛 Troubleshooting

### Hotkeys Don't Work in Games
**Solution:** Run as Administrator!
- Right-click app/exe → "Run as administrator"
- Or set compatibility → Always run as admin

### Can't Hear Sounds in Headphones
**Solution:** Set headphone output in Settings
- Click ⚙ Settings
- Set "Headphone Output" to your speakers/headphones
- Adjust "🎧 Headphone Volume" slider

### Others Can't Hear Me
**Solution:** Check mic volume
- Increase "🎤 Your Mic Volume" slider
- Make sure real mic is selected in Settings

### Sounds Are Distorted
**Solution:** Lower volumes
- Reduce per-sound volume (slider under each sound)
- Reduce mic volume if you're too loud
- Total mix shouldn't exceed 1.0

### VB Cable Not Detected
**Solution:** 
1. Check if VB Cable is installed (run `check_vb_cable.py`)
2. Restart computer after VB Cable install
3. Run soundboard as administrator

### Sound Keeps Playing
**Solution:** Click "⛔ Stop All" button or press hotkey again

## 🔨 Building an EXE

### For Personal Use
```bash
build.bat
```
Your exe will be in `dist/Soundboard.exe`

### For Distribution
See `DISTRIBUTION_GUIDE.md` for details on:
- Creating installers
- Bundling VB Cable
- Licensing considerations

## ⚖️ Legal & Distribution

### This Soundboard
- Free to use and modify
- Share with friends!

### VB-Audio Cable
- Free for personal use
- Required separate install
- See `DISTRIBUTION_GUIDE.md` for distribution options

## 🙏 Credits

**Built with:**
- Python 3.x
- tkinter (GUI)
- sounddevice (Audio I/O)  
- librosa (Audio processing)
- keyboard (Global hotkeys)
- numpy (Audio math)

**Requires:**
- VB-Audio Cable (Virtual audio routing)

---

Made with 💚 for the gaming community!