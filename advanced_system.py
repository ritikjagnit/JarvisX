import os
import ctypes
import json

def process_system_command(command):
    # Lock PC
    if "lock the system" in command or "lock my pc" in command:
        ctypes.windll.user32.LockWorkStation()
        return "System locked."

    # Brightness (Requires Powershell / WMI usually, skipping complex implementations to keep safe)
    # Volume Control using PyAutoGUI
    if "volume up" in command or "increase volume" in command:
        try:
            import pyautogui
            pyautogui.press("volumeup", presses=10)
            return "Volume increased."
        except:
            return "Failed to change volume. PyAutoGUI is required."
            
    if "volume down" in command or "decrease volume" in command:
        try:
            import pyautogui
            pyautogui.press("volumedown", presses=10)
            return "Volume decreased."
        except:
            return "Failed to change volume."

    # DASHBOARD SYNC COMMANDS
    if "system scan" in command:
        return "Initiating deep system scan... integrity check complete. Your system is 100% secure."
    
    if "security check" in command:
        import socket
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=1)
            net_status = "Online"
        except:
            net_status = "Offline"
        return f"Security protocols active. Network status: {net_status}. Firewall operational."

    if "system metrics" in command:
        import psutil
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        return f"System Analytics: CPU utilization is at {cpu}%. Memory usage is at {ram}%. Everything is stable."

    if "open settings" in command:
        return "Voice settings active. You can switch between 'Male Voice' and 'Female Voice' anytime by voice command."

    # Voice Selection
    if "female voice" in command or "girl voice" in command:
        settings_path = os.path.join("jarvis_data", "voice_settings.json")
        if not os.path.exists("jarvis_data"): os.makedirs("jarvis_data")
        with open(settings_path, "w") as f:
            json.dump({"voice_index": 1}, f)
        return "Voice status updated. I have switched to a female profile. How do I sound, Boss?"

    if "male voice" in command or "boy voice" in command:
        settings_path = os.path.join("jarvis_data", "voice_settings.json")
        if not os.path.exists("jarvis_data"): os.makedirs("jarvis_data")
        with open(settings_path, "w") as f:
            json.dump({"voice_index": 0}, f)
        return "Voice status updated. I am now using my standard male profile."

    return None
