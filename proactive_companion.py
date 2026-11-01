import os
import sys
import time
import random
import ctypes
import threading
from PyQt6.QtCore import QThread, pyqtSignal

# Global state for pending proactive action confirmation & user idle tracking
PENDING_PROACTIVE_ACTION = None
PENDING_ACTION_LOCK = threading.Lock()
LAST_USER_ACTIVITY_TIME = time.time()

def update_last_user_activity():
    """Call this function whenever the user types, gives a command, or interacts."""
    global LAST_USER_ACTIVITY_TIME
    LAST_USER_ACTIVITY_TIME = time.time()

def get_idle_time_seconds():
    """Returns how many seconds the user has been idle since their last command."""
    return time.time() - LAST_USER_ACTIVITY_TIME

def get_active_window_title():
    """Returns the title of the currently focused window on Windows OS."""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return "Desktop"
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return "Desktop"
        buff = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
        return buff.value or "Desktop"
    except Exception:
        return "Desktop"

def set_pending_action(action):
    global PENDING_PROACTIVE_ACTION
    with PENDING_ACTION_LOCK:
        PENDING_PROACTIVE_ACTION = action

def get_and_clear_pending_action():
    global PENDING_PROACTIVE_ACTION
    with PENDING_ACTION_LOCK:
        action = PENDING_PROACTIVE_ACTION
        PENDING_PROACTIVE_ACTION = None
        return action

import json

# Multi-lingual proactive companion prompts
DYNAMIC_PROMPT_POOLS_EN = {
    "code": [
        ("Shravani, I see you are coding in VS Code. Should I run System Metrics and performance test?", "system metrics"),
        ("VS Code is open Shravani! Should I run a System Audit on your code environment?", "system metrics"),
        ("Intense coding session detected Shravani! Shall I open your Astro Profile & AI Identity Dossier?", "FACE_DOSSIER_OPEN"),
        ("Python script editing active. Shall I start the Duplicate File Scanner?", "DUPLICATE_FINDER_OPEN"),
    ],
    "chrome": [
        ("Shravani, web research active. Shall I open the Real-Time Tech News & Web Research module?", "NEWS_RESEARCHER_OPEN"),
        ("Chrome active Shravani! Shall I summarize the latest Tech News digest for you?", "NEWS_RESEARCHER_OPEN"),
        ("Browsing active Shravani. Shall I open Encrypted Cyber Vault for your logins?", "CYBER_VAULT_OPEN"),
    ],
    "word": [
        ("Shravani, drafting document. Shall I open Meeting Notes Generator for you?", "MEETING_NOTES_OPEN"),
        ("Word document active Shravani. Shall I start AI Resume Reviewer & ATS Score Evaluator?", "RESUME_ANALYZER_OPEN"),
    ],
    "general": [
        ("Shravani, you have been working hard. Shall I open Cyber Vault for your passwords?", "CYBER_VAULT_OPEN"),
        ("SHRIVA AI OS online Shravani! Shall I open Astro Profile & AI Identity Scanner?", "FACE_DOSSIER_OPEN"),
        ("All systems optimal Shravani. Shall I run Duplicate File Cleaner?", "DUPLICATE_FINDER_OPEN"),
        ("Shravani, shall I open AI Mock Interview Coach for practice?", "INTERVIEW_COACH_OPEN"),
    ],
    "ultron": [
        ("Ultron Defense Core observing workspace. Activate Webcam Security Intruder scanner Shravani?", "INTRUDER_DETECT_START"),
        ("Workspace activity under surveillance Shravani. Start Security Defense Monitor?", "INTRUDER_DETECT_START"),
    ]
}

DYNAMIC_PROMPT_POOLS_HI = {
    "code": [
        ("श्रावणी, मैं देख रहा हूँ आप VS Code में कोडिंग कर रहे हैं। क्या मैं सिस्टम मीट्रिक्स रन कर दूँ?", "system metrics"),
        ("VS Code ओपन है श्रावणी! क्या मैं आपके कोड एनवायरनमेंट का सिस्टम ऑडिट रन कर दूँ?", "system metrics"),
        ("कोडिंग चल रही है श्रावणी! क्या मैं एस्ट्रो प्रोफाइल और फेस स्कैनर ओपन कर दूँ?", "FACE_DOSSIER_OPEN"),
        ("पायथन स्क्रिप्ट एक्टिव है। क्या मैं डुप्लीकेट फाइल स्कैनर स्टार्ट कर दूँ?", "DUPLICATE_FINDER_OPEN"),
    ],
    "chrome": [
        ("श्रावणी, क्रोम पर रिसर्च चल रही है। क्या मैं रियल-टाइम टेक न्यूज़ मॉड्यूल खोल दूँ?", "NEWS_RESEARCHER_OPEN"),
        ("क्रोम एक्टिव है श्रावणी! क्या मैं लेटेस्ट टेक न्यूज़ समराइज कर दूँ?", "NEWS_RESEARCHER_OPEN"),
        ("ब्राउज़िंग चल रही है श्रावणी। क्या मैं साइबर वॉल्ट ओपन कर दूँ लॉगिन के लिए?", "CYBER_VAULT_OPEN"),
    ],
    "word": [
        ("श्रावणी, डॉक्यूमेंट लिख रहे हैं। क्या मैं मीटिंग नोट्स जनरेटर खोल दूँ?", "MEETING_NOTES_OPEN"),
        ("वर्ड डॉक्यूमेंट एक्टिव है श्रावणी। क्या मैं AI रिज़्यूमे रिव्युअर स्टार्ट कर दूँ?", "RESUME_ANALYZER_OPEN"),
    ],
    "general": [
        ("श्रावणी, आप काफी देर से एक्टिव हैं। क्या मैं पासवर्ड्स के लिए साइबर वॉल्ट खोल दूँ?", "CYBER_VAULT_OPEN"),
        ("SHRIVA AI ऑनलाइन है श्रावणी! क्या मैं एस्ट्रो प्रोफाइल स्कैनर ओपन कर दूँ?", "FACE_DOSSIER_OPEN"),
        ("सारे सिस्टम ओके हैं श्रावणी। क्या मैं डुप्लीकेट फाइल क्लीनर रन कर दूँ?", "DUPLICATE_FINDER_OPEN"),
        ("श्रावणी, क्या मैं AI मॉक इंटरव्यू कोच ओपन कर दूँ प्रैक्टिस के लिए?", "INTERVIEW_COACH_OPEN"),
    ],
    "ultron": [
        ("अल्ट्रॉन डिफेन्स कोर ऑनलाइन है। क्या वेबकैम सिक्योरिटी स्कैनर एक्टिव कर दूँ श्रावणी?", "INTRUDER_DETECT_START"),
    ]
}

DYNAMIC_PROMPT_POOLS_MR = {
    "code": [
        ("श्रावणी, मी पाहत आहे तुम्ही VS Code मध्ये कोडिंग करत आहात. मी सिस्टिम मीट्रिक्स रन करू का?", "system metrics"),
        ("VS Code ओपन आहे श्रावणी! मी सिस्टिम ऑडिट टेस्ट सुरू करू का?", "system metrics"),
        ("उत्तम कोडिंग सुरू आहे श्रावणी! मी अ‍ॅस्ट्रो प्रोफाइल आणि फेस स्कॅनर ओपन करू का?", "FACE_DOSSIER_OPEN"),
        ("मी डुप्लिकेट फाइल स्कॅनर सुरू करू का, श्रावणी?", "DUPLICATE_FINDER_OPEN"),
    ],
    "chrome": [
        ("श्रावणी, क्रोमवर संशोधन सुरू आहे. मी रिअल-टाइम टेक न्यूज मॉड्युल उघडू का?", "NEWS_RESEARCHER_OPEN"),
        ("क्रोम अ‍ॅक्टिव्ह आहे श्रावणी! मी सायबर वॉल्ट ओपन करू का लॉगीन्ससाठी?", "CYBER_VAULT_OPEN"),
    ],
    "word": [
        ("श्रावणी, दस्तऐवज लिहित आहात. मी मीटिंग नोट्स जनरेटर उघडू का?", "MEETING_NOTES_OPEN"),
        ("वर्ड दस्तऐवज अ‍ॅक्टिव्ह आहे श्रावणी. मी AI रिझ्युम रिव्ह्यूअर सुरू करू का?", "RESUME_ANALYZER_OPEN"),
    ],
    "general": [
        ("श्रावणी, तुम्ही खूप वेळ काम करत आहात. मी पासवर्ड्ससाठी सायबर वॉल्ट उघडू का?", "CYBER_VAULT_OPEN"),
        ("SHRIVA AI ऑनलाइन आहे श्रावणी! मी अ‍ॅस्ट्रो प्रोफाइल स्कॅनर ओपन करू का?", "FACE_DOSSIER_OPEN"),
        ("सर्व सिस्टिम्स उत्तम आहेत श्रावणी. मी डुप्लिकेट फाइल क्लिनर रन करू का?", "DUPLICATE_FINDER_OPEN"),
    ],
    "ultron": [
        ("अल्ट्रॉन सुरक्षा प्रोटोकॉल ऑनलाइन आहे, श्रावणी. सिक्युरिटी स्कॅनर सुरू करू का?", "INTRUDER_DETECT_START"),
    ]
}

class ProactiveCompanionThread(QThread):
    """
    Background Thread that monitors user activity, generates dynamic non-repeating multi-lingual messages,
    and registers pending action confirmations.
    """
    companion_message = pyqtSignal(str, str) # Emits (message_text, action_intent)

    def __init__(self, interval_sec=45):
        super().__init__()
        self.interval = interval_sec
        self.running = False
        self.is_ultron = False
        self.last_used_indices = {}

    def set_ultron_mode(self, is_ultron):
        self.is_ultron = is_ultron

    def _get_dynamic_prompt(self, category):
        pool = DYNAMIC_PROMPT_POOLS_EN.get(category, DYNAMIC_PROMPT_POOLS_EN["general"])
        if self.is_ultron and "ultron" in DYNAMIC_PROMPT_POOLS_EN:
            pool = DYNAMIC_PROMPT_POOLS_EN["ultron"]

        if not pool:
            return None, None

        last_idx = self.last_used_indices.get(category, -1)
        available_indices = [i for i in range(len(pool)) if i != last_idx]
        if not available_indices:
            available_indices = list(range(len(pool)))

        chosen_idx = random.choice(available_indices)
        self.last_used_indices[category] = chosen_idx
        return pool[chosen_idx]

    def run(self):
        self.running = True
        print(f"[PROACTIVE COMPANION] Dynamic Hindi Proactive Thread started. Interval: {self.interval}s")
        
        while self.running:
            # Wait for interval (check every 1 second for clean stop signal)
            for _ in range(int(self.interval)):
                if not self.running:
                    return
                time.sleep(1.0)

            if not self.running:
                return

            try:
                # User Activity Check: ONLY talk if user has been completely idle for >= 60 seconds (1 minute)!
                idle_sec = time.time() - LAST_USER_ACTIVITY_TIME
                if idle_sec < 60:
                    print(f"[PROACTIVE COMPANION] User is actively working (Idle: {int(idle_sec)}s < 60s). Proactive companion quiet.")
                    continue

                active_title = get_active_window_title()
                title_lower = active_title.lower()
                print(f"[PROACTIVE COMPANION] User IDLE for {int(idle_sec)}s >= 60s. Checking Active Window: '{active_title}'")

                # Determine category
                if self.is_ultron:
                    category = "ultron"
                elif "code" in title_lower or "py" in title_lower or "visual studio" in title_lower or "main.py" in title_lower:
                    category = "code"
                elif "chrome" in title_lower or "edge" in title_lower or "browser" in title_lower:
                    category = "chrome"
                elif "word" in title_lower or "document" in title_lower or "notepad" in title_lower:
                    category = "word"
                else:
                    category = "general"

                msg, action = self._get_dynamic_prompt(category)
                set_pending_action(action)
                print(f"[PROACTIVE COMPANION] Spoke: '{msg}' | Proposed Action: '{action}'")

                # Emit to UI (main thread will handle speech and display)
                self.companion_message.emit(msg, action)

            except Exception as e:
                print(f"[PROACTIVE COMPANION ERROR] {e}")

    def stop(self):
        self.running = False
        self.wait()
