# updater.py - Auto-update checker
import json
import webbrowser
import threading
from tkinter import messagebox

# Import version from single source of truth
from version import __version__

CURRENT_VERSION = __version__
UPDATE_CHECK_URL = "https://raw.githubusercontent.com/patrick-1480/soundboard-pro/refs/heads/main/version.json"


def check_for_updates():
    """
    Check if a new version is available
    
    Returns:
        dict or None: Update info if available, None otherwise
    """
    try:
        import urllib.request
        
        with urllib.request.urlopen(UPDATE_CHECK_URL, timeout=5) as response:
            data = json.loads(response.read().decode())
        
        latest_version = data.get('version', '0.0.0')
        
        # Compare versions
        if _is_newer_version(latest_version, CURRENT_VERSION):
            return data
        
        return None
        
    except Exception as e:
        print(f"Update check failed: {e}")
        return None


def _is_newer_version(latest, current):
    """
    Compare version strings
    
    Args:
        latest: Latest version string (e.g. "3.0.0")
        current: Current version string (e.g. "2.2.0")
    
    Returns:
        bool: True if latest is newer than current
    """
    try:
        latest_parts = [int(x) for x in latest.split('.')]
        current_parts = [int(x) for x in current.split('.')]
        
        # Pad with zeros if needed
        while len(latest_parts) < 3:
            latest_parts.append(0)
        while len(current_parts) < 3:
            current_parts.append(0)
        
        return latest_parts > current_parts
        
    except:
        return False


def show_update_notification(root, update_data):
    """
    Show update notification dialog
    
    Args:
        root: Tkinter root window
        update_data: Update information dictionary
    """
    version = update_data.get('version', 'Unknown')
    changelog = update_data.get('changelog', 'No changelog available')
    download_url = update_data.get('download_url', '')
    required = update_data.get('required', False)
    
    message = f"Version {version} is available!\n\n"
    message += "What's New:\n"
    message += changelog
    message += "\n\nWould you like to download it now?"
    
    title = "🎉 Update Available!" if not required else "⚠️ Required Update"
    
    result = messagebox.askyesno(title, message, parent=root)
    
    if result and download_url:
        webbrowser.open(download_url)


def check_updates_in_background(root):
    """
    Check for updates in background thread
    
    Args:
        root: Tkinter root window
    """
    def check():
        # Wait a bit before checking
        import time
        time.sleep(2)
        
        update_data = check_for_updates()
        
        if update_data:
            # Show notification in main thread
            root.after(0, lambda: show_update_notification(root, update_data))
    
    thread = threading.Thread(target=check, daemon=True)
    thread.start()


# For testing
if __name__ == "__main__":
    print(f"Current version: {CURRENT_VERSION}")
    print("Checking for updates...")
    
    update = check_for_updates()
    if update:
        print(f"Update available: {update['version']}")
        print(f"Changelog: {update['changelog']}")
    else:
        print("You're up to date!")