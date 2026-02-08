# updater.py - Simple auto-update checker
import json
import webbrowser
import threading
from tkinter import messagebox

CURRENT_VERSION = "2.0.0"
UPDATE_CHECK_URL = "https://raw.githubusercontent.com/yourusername/soundboard-pro/main/version.json"

# Or use your own website:
# UPDATE_CHECK_URL = "https://yourwebsite.com/soundboard/version.json"

def parse_version(v):
    """Convert version string to comparable tuple"""
    return tuple(map(int, v.split('.')))

def check_for_updates():
    """Check if a new version is available"""
    try:
        import requests
        response = requests.get(UPDATE_CHECK_URL, timeout=5)
        data = response.json()
        
        latest_version = data["version"]
        
        if parse_version(latest_version) > parse_version(CURRENT_VERSION):
            return {
                "available": True,
                "version": latest_version,
                "download_url": data["download_url"],
                "changelog": data.get("changelog", "Bug fixes and improvements"),
                "required": data.get("required", False)
            }
    except Exception as e:
        print(f"Update check failed: {e}")
        return None
    
    return {"available": False}

def show_update_notification(update_info, parent_window=None):
    """Show update notification dialog"""
    if not update_info or not update_info.get("available"):
        return
    
    version = update_info["version"]
    changelog = update_info["changelog"]
    url = update_info["download_url"]
    required = update_info.get("required", False)
    
    if required:
        title = "⚠️ Required Update Available"
        message = f"Soundboard Pro v{version} is now available.\n\n"
        message += "This update is required to continue using the app.\n\n"
        message += f"What's new:\n{changelog}\n\n"
        message += "Click OK to download the update."
        
        if messagebox.showinfo(title, message, parent=parent_window):
            webbrowser.open(url)
            import sys
            sys.exit(0)
    else:
        title = "Update Available"
        message = f"Soundboard Pro v{version} is now available!\n\n"
        message += f"What's new:\n{changelog}\n\n"
        message += "Would you like to download it now?"
        
        if messagebox.askyesno(title, message, parent=parent_window):
            webbrowser.open(url)

def check_updates_in_background(parent_window=None, silent=True):
    """Check for updates in a background thread"""
    def check():
        update_info = check_for_updates()
        if update_info and update_info.get("available"):
            # Schedule UI update on main thread
            if parent_window:
                parent_window.after(0, lambda: show_update_notification(update_info, parent_window))
        elif not silent:
            if parent_window:
                parent_window.after(0, lambda: messagebox.showinfo("No Updates", "You're running the latest version!"))
    
    thread = threading.Thread(target=check, daemon=True)
    thread.start()

# Example usage in app.py:
# from updater import check_updates_in_background
# 
# After creating root window:
# check_updates_in_background(root)