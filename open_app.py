import os
import subprocess
from voice_engine import speak
import glob

# Common Aliases mapping spoken name to exact exe or URI protocol
ALIASES = {
    "whatsapp": "whatsapp:",
    "vscode": "visual studio code",
    "visual studio code": "visual studio code",
    "browser": "chrome",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "calculator": "calc",
    "settings": "ms-settings:",
    "setting": "ms-settings:",
    "task manager": "taskmgr",
    "control panel": "control",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "terminal": "cmd.exe",
    "my computer": "explorer",
    "this pc": "explorer",
    "file explorer": "explorer",
    "paint": "mspaint",
    "notepad": "notepad",
    "camera": "microsoft.windows.camera:",
}

def open_app(app_name):
    app_name = app_name.lower().strip()
    print(f"[DEBUG-APP] Raw Open Request: '{app_name}'")
    
    # 1. Alias translation
    for alias, true_name in ALIASES.items():
        if alias in app_name:
            app_name = true_name
            break
    
    print(f"[DEBUG-APP] Attempting to open translated format: '{app_name}'")

    # Handle URI Protocol (e.g. ms-settings:)
    if ":" in app_name:
        try:
            os.system(f'start {app_name}')
            return True
        except Exception:
            pass

    # 2. Hardcoded Common exact paths
    common_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        os.path.expandvars(r"%LocalAppData%\Programs\Microsoft VS Code\Code.exe")
    ]
    for path in common_paths:
        if app_name in path.lower() and os.path.exists(path):
            print(f"[DEBUG-APP] Found exact path match: {path}")
            subprocess.Popen(path)
            return True

    # 3. Start Menu Search (Deep Search)
    print(f"[DEBUG-APP] Searching Start Menu for {app_name}")
    start_menu_paths = [
        os.path.join(os.environ.get("PROGRAMDATA", "C:\\ProgramData"), "Microsoft\\Windows\\Start Menu\\Programs"),
        os.path.join(os.environ.get("PUBLIC", r"C:\Users\Public"), "Desktop"),
        os.path.expanduser("~/Desktop") 
    ]
    
    clean_target = app_name.replace(" ", "")
    for path in start_menu_paths:
        if not os.path.exists(path): continue
        for root, dirs, files in os.walk(path):
            for file in files:
                f_clean = file.lower().replace(" ", "")
                if clean_target in f_clean and file.endswith(".lnk"):
                    app_path = os.path.join(root, file)
                    print(f"[DEBUG-APP] Found App Shortcut: {app_path}")
                    try:
                        os.startfile(app_path)
                        return True
                    except Exception:
                        continue
                
                # Check for direct EXEs in these folders too
                if clean_target in f_clean and file.endswith(".exe"):
                    app_path = os.path.join(root, file)
                    print(f"[DEBUG-APP] Found Direct EXE: {app_path}")
                    try:
                        subprocess.Popen(app_path)
                        return True
                    except Exception:
                        continue

    # 4. Fallback execution via Windows Shell start
    try:
        os.system(f'start "" "{app_name}"')
        return True
    except Exception as e:
        print(f"[DEBUG-APP] Error opening '{app_name}': {e}")
        return False
