"""
Notepad automation and file management for JARVIS AI Letter Writer.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import pyperclip
except ImportError:
    pyperclip = None

def open_notepad():
    """Opens Windows Notepad and waits until focused."""
    try:
        if sys.platform.startswith("win"):
            subprocess.Popen(["notepad.exe"])
        else:
            subprocess.Popen(["gedit"]) # Linux fallback if needed
        time.sleep(1.5) # Allow Notepad window time to launch and focus
        return True
    except Exception as e:
        print(f"[NOTEPAD AUTOMATION ERROR] Failed to launch Notepad: {e}")
        return False

def type_text_into_notepad(text: str) -> bool:
    """
    Types or pastes full formatted text into the active Notepad window,
    preserving exact line breaks and spacing smoothly.
    """
    if not text:
        return False

    try:
        # Use pyperclip + Ctrl+V for flawless line breaks & zero character drops if available
        if pyperclip is not None:
            pyperclip.copy(text)
            time.sleep(0.3)
            if pyautogui is not None:
                pyautogui.hotkey('ctrl', 'v')
                return True

        # Fallback to pyautogui write if pyperclip is not available
        if pyautogui is not None:
            # Type line by line to preserve line breaks reliably
            lines = text.split("\n")
            for line in lines:
                if line:
                    pyautogui.write(line, interval=0.005)
                pyautogui.press('enter')
            return True
        else:
            print("[NOTEPAD AUTOMATION WARNING] Neither pyperclip nor pyautogui is available for typing.")
            return False

    except Exception as e:
        print(f"[NOTEPAD AUTOMATION ERROR] Exception during typing: {e}")
        return False

def open_notepad_and_type(text: str) -> tuple[bool, str]:
    """
    Main helper to launch Notepad and type the given letter.
    Returns (success, status_message).
    """
    if not open_notepad():
        return False, "Unable to open Notepad."

    success = type_text_into_notepad(text)
    if success:
        return True, "Your letter has been written in Notepad."
    else:
        return False, "Failed to type letter into Notepad due to automation error."

def save_letter_file(text: str, filename_hint: str = "JARVIS_Letter") -> tuple[bool, str]:
    """
    Saves the generated letter into Documents/JARVIS Letters/ as a .txt file.
    Creates directory automatically if it does not exist.
    """
    try:
        docs_dir = Path.home() / "Documents" / "JARVIS Letters"
        docs_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize filename
        clean_name = "".join(c for c in filename_hint if c.isalnum() or c in (" ", "_", "-")).strip()
        if not clean_name:
            clean_name = "JARVIS_Letter"
        clean_name = clean_name.replace(" ", "_")

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{clean_name}_{timestamp}.txt"
        file_path = docs_dir / filename

        file_path.write_text(text, encoding="utf-8")
        print(f"[LETTER SAVED] Successfully saved letter to: {file_path}")
        return True, str(file_path)
    except Exception as e:
        print(f"[LETTER SAVE ERROR] Could not save letter: {e}")
        return False, str(e)
