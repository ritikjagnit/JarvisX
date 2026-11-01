import subprocess
import os
import json
import threading

class AndroidBridge:
    """
    PC-to-Android Control Engine via Wireless ADB & Web Push:
    Allows PC voice commands to control physical Android/iOS phones over Wi-Fi.
    """
    def __init__(self):
        self.adb_available = self._check_adb()

    def _check_adb(self):
        try:
            res = subprocess.run(["adb", "version"], capture_output=True, text=True, timeout=2)
            return res.returncode == 0
        except Exception:
            return False

    def get_connected_devices(self):
        if not self.adb_available:
            return []
        try:
            res = subprocess.run(["adb", "devices"], capture_output=True, text=True)
            lines = res.stdout.strip().split('\n')[1:]
            devices = [line.split('\t')[0] for line in lines if '\tdevice' in line]
            return devices
        except Exception:
            return []

    def open_app_on_phone(self, app_name):
        app_map = {
            "whatsapp": "com.whatsapp",
            "youtube": "com.google.android.youtube",
            "chrome": "com.android.chrome",
            "settings": "com.android.settings",
            "camera": "com.android.camera2",
            "instagram": "com.instagram.android",
            "spotify": "com.spotify.music"
        }
        package = app_map.get(app_name.lower().strip())
        if not package:
            package = f"com.{app_name.lower().strip()}"

        devices = self.get_connected_devices()
        if devices:
            try:
                cmd = f"adb shell monkey -p {package} -c android.intent.category.LAUNCHER 1"
                subprocess.run(cmd, shell=True, capture_output=True)
                return f"Opening '{app_name}' natively on Android device via ADB!"
            except Exception as e:
                return f"Failed to open '{app_name}' via ADB: {e}"
        else:
            # Fallback to Mobile Remote Web Push Action
            from mobile_remote_server import push_mobile_action
            if "youtube" in app_name.lower():
                push_mobile_action("open_url", "https://youtube.com")
            elif "whatsapp" in app_name.lower():
                push_mobile_action("open_url", "https://web.whatsapp.com")
            else:
                push_mobile_action("vibrate", "500")
            return f"Action 'Open {app_name}' pushed to connected mobile phone web link!"

    def ring_phone(self):
        from mobile_remote_server import push_mobile_action
        push_mobile_action("ring_alarm", "High Alarm")
        devices = self.get_connected_devices()
        if devices:
            try:
                subprocess.run("adb shell input keyevent 24", shell=True, capture_output=True) # Max Volume
            except Exception: pass
        return "Ringing alarm on connected mobile phone now!"

    def vibrate_phone(self):
        from mobile_remote_server import push_mobile_action
        push_mobile_action("vibrate", "800")
        return "Vibrating connected mobile phone!"

android_bridge = AndroidBridge()
