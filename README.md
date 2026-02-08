# 🎵 Soundboard Pro

Professional audio soundboard with global hotkeys for Windows.

![Version](https://img.shields.io/badge/version-3.2.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows-blue)

## ✨ Features

- 🎮 **Global Hotkeys** - Works in games, Discord, anywhere
- 🎤 **Voice Passthrough** - Talk while sounds play
- 🎧 **Dual Audio** - Hear sounds in headphones + send to virtual mic
- 🎨 **Modern UI** - Sleek dark theme with smooth animations
- 💾 **Auto-Save** - All settings, volumes, and hotkeys persist
- 🔄 **Auto-Update** - Get notified of new versions
- 🎚️ **Monitor Toggle** - Choose whether to hear yourself

## 📥 Download

**[Download Latest Release (v3.2.0)](https://github.com/patrick-1480/soundboard-pro/releases/latest)**

Download `SoundboardPro_Setup_v3.2.0.exe` and run the installer.

## 📋 Requirements

- **Windows 10 or 11** (64-bit)
- **VB-Audio Cable** (required): [Download here](https://vb-audio.com/Cable/)
- **Run as Administrator** for global hotkeys to work in games

## 🚀 Quick Start

1. Download and install VB-Audio Cable
2. Restart your computer (required after VB Cable install)
3. Download Soundboard Pro installer
4. Run `SoundboardPro_Setup_v3.2.0.exe`
5. Launch Soundboard Pro
6. Click Settings and configure:
   - **Microphone Input:** Your physical microphone
   - **Virtual Mic Output:** CABLE Input
   - **Headphone Output:** Your speakers/headphones
7. Click "Apply & Restart Audio"
8. Add sounds and set hotkeys!

## 🎮 Discord/Game Setup

**In Discord (or your game):**
1. Go to Voice Settings
2. Set Input Device to **CABLE Output**
3. Your friends will now hear your sounds + voice!

## 📖 Features Guide

### Global Hotkeys
- Set a hotkey for each sound (F1, Ctrl+1, etc.)
- Works even when app is in background
- Works in games, Discord, anywhere
- **Note:** Run as Administrator for hotkeys in games

### Voice Passthrough
- Your voice and sounds are mixed together
- Both go to Discord/game simultaneously
- Adjust volumes independently

### Monitor Toggle
- **ON:** Hear yourself in headphones
- **OFF:** Only hear sounds, not your voice
- Your friends always hear you (toggle only affects what YOU hear)

### Volume Controls
- **Microphone:** How loud your voice is to others
- **Headphones:** How loud you hear everything
- **Per-Sound:** Individual volume for each sound

## 🐛 Troubleshooting

### "No audio devices found"
- Install VB-Audio Cable
- Restart your computer
- Open Settings and select devices

### Hotkeys don't work in games
- Right-click Soundboard Pro
- Run as Administrator
- Hotkeys should now work everywhere

### Sounds are too quiet/loud
- Adjust per-sound volume sliders
- Adjust master microphone volume
- Check Discord/game input sensitivity

### Settings don't save
- App saves to `%APPDATA%\SoundboardPro`
- Make sure folder isn't read-only
- Run as Administrator if needed

## 🔄 Updating

The app checks for updates automatically on launch. When a new version is available:
1. Click "Yes" to download
2. Run the new installer
3. Your settings are preserved!

## 🤝 Contributing

Contributions welcome! Feel free to:
- Report bugs in [Issues](https://github.com/patrick-1480/soundboard-pro/issues)
- Submit pull requests
- Suggest features

## 📄 License

MIT License - See [LICENSE](LICENSE.txt)

## 🙏 Acknowledgments

Built with:
- [Python](https://python.org)
- [sounddevice](https://python-sounddevice.readthedocs.io/)
- [librosa](https://librosa.org/)
- [keyboard](https://github.com/boppreh/keyboard)

## ❓ FAQ

**Q: Is this free?**
A: Yes! Completely free and open source.

**Q: Does it work on Mac/Linux?**
A: Currently Windows only. macOS support may come in future.

**Q: Is it safe?**
A: Yes! All code is open source and auditable. Windows may show a warning because the app isn't code-signed (costs $300/year).

**Q: Can I use it for streaming?**
A: Absolutely! Works great with OBS, Streamlabs, etc.

**Q: How many sounds can I add?**
A: Unlimited! Limited only by your disk space.

**Q: Can I use .mp3 files?**
A: Yes! Supports .mp3, .wav, .ogg, and .flac

---

Made with ❤️ by [Patrick](https://github.com/patrick-1480)

⭐ Star this repo if you find it useful!