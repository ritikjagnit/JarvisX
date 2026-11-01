import os
import sys
import base64
import re
import requests
from PIL import Image

from api_keys import GEMINI_API_KEY, OPENAI_API_KEY

SCREENSHOT_PATH = "screenshot.jpg"

def capture_screenshot(filename=SCREENSHOT_PATH):
    """
    Ultra-reliable screen capture using PyQt6 primaryScreen grabWindow,
    with fallback to PIL ImageGrab / pyautogui.
    """
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QGuiApplication
        
        # Check if a QApplication instance exists or create a temporary one
        app = QApplication.instance()
        created_app = False
        if not app:
            app = QApplication(sys.argv)
            created_app = True

        screen = QGuiApplication.primaryScreen()
        if screen:
            pixmap = screen.grabWindow(0)
            # Resize if very high resolution
            if pixmap.width() > 1920:
                pixmap = pixmap.scaledToWidth(1920)
            pixmap.save(filename, "JPEG", 75)
            print(f"[SCREENSHOT] PyQt6 captured {pixmap.width()}x{pixmap.height()} -> {filename}")
            return filename
    except Exception as e:
        print(f"[SCREENSHOT] PyQt6 capture fallback triggered: {e}")

    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        if img.width > 1920:
            aspect = img.height / img.width
            img = img.resize((1920, int(1920 * aspect)), Image.Resampling.LANCZOS)
        img.convert("RGB").save(filename, "JPEG", quality=75)
        print(f"[SCREENSHOT] PIL captured screen -> {filename}")
        return filename
    except Exception as e:
        print(f"[SCREENSHOT] Capture error: {e}")
        return None


def analyze_screenshot(image_path, prompt):
    """Sends the screenshot to Gemini Vision (gemini-3.1-flash-lite / gemini-3.5-flash) with fallback."""
    if not os.path.exists(image_path):
        return "There is no screenshot available to analyze."

    try:
        with open(image_path, "rb") as f:
            img_data = f.read()
        img_b64 = base64.b64encode(img_data).decode("utf-8")
    except Exception as e:
        return f"Failed to read the screenshot file: {e}"

    # 1. Try Gemini Vision models (gemini-3.5-flash is fast & reliable)
    if GEMINI_API_KEY:
        models = ["gemini-3.5-flash", "gemini-flash-latest", "gemini-3.1-flash-lite"]
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inlineData": {
                            "mimeType": "image/jpeg",
                            "data": img_b64
                        }
                    }
                ]
            }]
        }

        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
            try:
                print(f"[SCREENSHOT] Querying Gemini Vision model: {model}...")
                response = requests.post(url, json=payload, headers=headers, timeout=15)
                if response.status_code == 200:
                    res_json = response.json()
                    candidates = res_json.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
                else:
                    print(f"[SCREENSHOT] Model {model} returned status {response.status_code}")
            except Exception as e:
                print(f"[SCREENSHOT] Gemini query error on {model}: {e}")

    # 2. Offline Fallback: OCR + Regex Stack Trace Detector
    try:
        import pytesseract
        text = pytesseract.image_to_string(Image.open(image_path))
        if "Traceback" in text:
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            err_line = lines[-1] if lines else "Unknown traceback"
            return f"Offline Code Scanner: Detected active Python traceback on screen: {err_line}"
        elif "Error" in text or "Exception" in text:
            match = re.search(r"(\w+Error:.*|\w+Exception:.*)", text)
            if match:
                return f"Offline Code Scanner: Detected active error on screen: {match.group(1)[:120]}"
    except Exception:
        pass

    return "Screen analyzed, but unable to reach AI vision servers. Please verify your internet connection."


def process_screenshot_command(command):
    """
    Processes natural language screen vision and code debugging requests.
    Examples:
    - "what is on my screen", "explain my screen", "what am i looking at"
    - "debug this code", "debug this error", "find the bug on my screen"
    - "explain this diagram", "what is this architecture"
    """
    cmd = command.lower().strip()

    is_debug = any(k in cmd for k in ["debug", "error on screen", "bug on screen", "fix code", "find bug", "code error", "exception on screen"])
    is_diagram = any(k in cmd for k in ["diagram", "architecture", "flowchart", "circuit", "chart on screen"])
    is_general = any(k in cmd for k in [
        "what is on my screen", "what's on my screen", "explain my screen",
        "explain screen", "analyze my screen", "analyze screen", "see my screen",
        "what am i looking at", "describe screen"
    ])

    if not (is_debug or is_diagram or is_general):
        return None

    path = capture_screenshot()
    if not path:
        return "I was unable to capture your screen display."

    if is_debug:
        prompt = (
            "You are JARVIS, an elite AI code debugger. Analyze the computer screen image carefully. "
            "Identify the active code, terminal error, or exception. "
            "State the exact error and give the 1-2 sentence solution directly."
        )
    elif is_diagram:
        prompt = (
            "You are JARVIS. Analyze the visual architecture, diagram, or flowchart displayed on the user's screen. "
            "Explain the system flow and key components in 2 concise sentences."
        )
    else:
        prompt = (
            "You are JARVIS, an advanced AI Desktop OS. Analyze the user's computer screen. "
            "Identify the active application and summarize what the user is working on in 2 short, direct sentences."
        )

    return analyze_screenshot(path, prompt)
