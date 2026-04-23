import os
from voice_engine import speak

APP_PROCESSES = {
    "chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "edge": "msedge.exe",
    "notepad": "notepad.exe",
    "calculator": "CalculatorApp.exe",
    "calc": "CalculatorApp.exe",
    "paint": "mspaint.exe",
    "vscode": "Code.exe",
    "visual studio code": "Code.exe",
    "youtube": "chrome.exe",
    "whatsapp": "WhatsApp.exe",
    "browser": "chrome.exe",
    "word": "WINWORD.EXE",
    "excel": "EXCEL.EXE"
}

def close_app(app_name):
    app_name = app_name.lower().strip()
    
    # 1. Check predefined mapping
    process_name = APP_PROCESSES.get(app_name)
    
    # 2. If not in mapping, try to find a running process that looks like the name
    if not process_name:
        try:
            import psutil
            print(f"[DEBUG-APP] Scanning active processes for '{app_name}'...")
            for proc in psutil.process_iter(['name']):
                p_name = proc.info['name'].lower()
                if app_name in p_name:
                    process_name = p_name
                    print(f"[DEBUG-APP] Dynamically identified process: {process_name}")
                    break
        except Exception as e:
            print(f"[DEBUG-APP] Process scan failed: {e}")

    # Fallback to appending .exe
    if not process_name:
        process_name = f"{app_name}.exe"
    
    print(f"[DEBUG-APP] Final termination target: '{process_name}'")
    
    try:
        # Using taskkill for forceful termination
        result = os.system(f"taskkill /f /im {process_name}")
        if result == 0:
            return True
        else:
            # Try one more time with exact name if user provided one
            return os.system(f"taskkill /f /im {app_name}") == 0
    except Exception as e:
        print(f"[DEBUG-APP] Error closing app: {e}")
        return False
