"""
Legacy bridge plugin for letter generation, delegating calls to the modular letter_writer package.
"""

import os
import time
import random
import datetime
import pyautogui

try:
    from letter_writer import process_letter_command as new_process_letter
except ImportError:
    new_process_letter = None

def generate_letter(command, user_name="Shravani", receiver_name="Sir/Madam"):
    """Legacy interface forwarding request to modular letter_writer."""
    if new_process_letter is not None:
        return new_process_letter(command)
    else:
        # Fallback to old behavior if package import fails
        os.system("start notepad")
        time.sleep(1.5)
        pyautogui.write("Letter content generated.", interval=0.01)