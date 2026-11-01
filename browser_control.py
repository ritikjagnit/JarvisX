import webbrowser
from urllib.parse import quote_plus

try:
    import pyautogui
    pyautogui.PAUSE = 0.05
    pyautogui.FAILSAFE = False
except ImportError:
    pyautogui = None

def process_browser_command(command, context_state=None):
    if not command:
        return None

    cmd = command.lower().strip()

    # ---------------- 1. SCREEN SCROLLING CONTROLS ----------------
    if any(k in cmd for k in ["scroll down", "scroll screen down", "scroll screen", "scroll page down", "page down"]):
        if pyautogui:
            pyautogui.scroll(-700)
            pyautogui.press('pagedown')
            return "Scrolling screen down."
        return "PyAutoGUI is not available for scrolling."

    if any(k in cmd for k in ["scroll up", "scroll screen up", "scroll page up", "page up"]):
        if pyautogui:
            pyautogui.scroll(700)
            pyautogui.press('pageup')
            return "Scrolling screen up."
        return "PyAutoGUI is not available for scrolling."

    if any(k in cmd for k in ["scroll top", "scroll to top", "go to top"]):
        if pyautogui:
            pyautogui.press('home')
            return "Scrolling to top."

    if any(k in cmd for k in ["scroll bottom", "scroll to bottom", "go to bottom"]):
        if pyautogui:
            pyautogui.press('end')
            return "Scrolling to bottom."

    # ---------------- 2. YOUTUBE & MEDIA PLAYBACK CONTROLS ----------------
    # (Only trigger toggle if command is exact media control, NOT song playback queries like 'play desi boy song')
    if cmd in ["pause video", "play video", "pause", "play", "stop video", "resume video", "pause music", "resume music"]:
        if pyautogui:
            pyautogui.press('k')
            return "Toggling video play pause."

    if any(k in cmd for k in ["mute video", "unmute video", "mute", "unmute"]):
        if pyautogui:
            pyautogui.press('m')
            return "Toggling audio mute."

    if any(k in cmd for k in ["full screen", "fullscreen", "exit fullscreen", "toggle fullscreen"]):
        if pyautogui:
            pyautogui.press('f')
            return "Toggling fullscreen mode."

    if any(k in cmd for k in ["theater mode", "theatre mode"]):
        if pyautogui:
            pyautogui.press('t')
            return "Toggling theater mode."

    if any(k in cmd for k in ["skip 10 seconds", "forward 10 seconds", "seek forward", "forward"]):
        if pyautogui:
            pyautogui.press('l')
            return "Seeking forward 10 seconds."

    if any(k in cmd for k in ["rewind 10 seconds", "back 10 seconds", "seek back", "rewind"]):
        if pyautogui:
            pyautogui.press('j')
            return "Rewinding 10 seconds."

    if any(k in cmd for k in ["next video", "play next video", "skip video"]):
        if pyautogui:
            pyautogui.hotkey('shift', 'n')
            return "Playing next video."

    if any(k in cmd for k in ["volume up", "increase volume", "louder"]):
        if pyautogui:
            pyautogui.press('up')
            return "Increasing volume."

    if any(k in cmd for k in ["volume down", "decrease volume", "lower volume", "quieter"]):
        if pyautogui:
            pyautogui.press('down')
            return "Decreasing volume."

    # ---------------- 3. BROWSER & TAB NAVIGATION ----------------
    if any(k in cmd for k in ["go back", "previous page", "back page"]):
        if pyautogui:
            pyautogui.hotkey('alt', 'left')
            return "Navigating back."

    if any(k in cmd for k in ["go forward", "next page", "forward page"]):
        if pyautogui:
            pyautogui.hotkey('alt', 'right')
            return "Navigating forward."

    if any(k in cmd for k in ["refresh page", "reload page", "refresh", "reload"]):
        if pyautogui:
            pyautogui.hotkey('ctrl', 'r')
            return "Reloading page."

    if any(k in cmd for k in ["close tab", "close browser tab"]):
        if pyautogui:
            pyautogui.hotkey('ctrl', 'w')
            return "Closing browser tab."

    if any(k in cmd for k in ["new tab", "open new tab"]):
        if pyautogui:
            pyautogui.hotkey('ctrl', 't')
            return "Opening new browser tab."

    # Helper for getting active language code
    import os, json
    lang_code = "en"
    settings_path = os.path.join("jarvis_data", "voice_settings.json")
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                lang_code = json.load(f).get("language", "en")
        except Exception:
            lang_code = "en"

    # ---------------- 4. WEBPAGE OPENING & SEARCH INTENTS ----------------
    if "youtube" in cmd and (any(k in cmd for k in ["open", "kholo", "khol", "kru", "skto", "ugha", "ughad", "chalu", "play", "start", "sathi"]) or cmd == "youtube"):
        webbrowser.open("https://youtube.com")
        if context_state is not None:
             context_state['last_platform'] = 'youtube'
        if lang_code == "hi":
            return "यूट्यूब खोला जा रहा है, श्रावणी।"
        elif lang_code == "mr":
            return "यूट्यूब सुरू केले जात आहे, श्रावणी."
        else:
            return "Opening YouTube."

    if "search youtube" in cmd or "youtube pe search" in cmd or "youtube vr search" in cmd:
        query = cmd.replace("search youtube", "").replace("youtube pe search", "").replace("youtube vr search", "").replace("search", "").strip()
        if not query:
            if lang_code == "hi": return "आप यूट्यूब पर क्या खोजना चाहते हैं?"
            if lang_code == "mr": return "तुम्हाला यूट्यूबवर काय शोधायचे आहे?"
            return "What do you want to search on YouTube?"
        webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
        if context_state is not None:
            context_state['last_platform'] = 'youtube'
        if lang_code == "hi": return f"यूट्यूब पर {query} खोजा जा रहा है।"
        if lang_code == "mr": return f"यूट्यूबवर {query} शोधले जात आहे."
        return f"Searching YouTube for {query}."

    if "search google" in cmd or "google pe search" in cmd or "google vr search" in cmd or "search for" in cmd:
        query = cmd.replace("search google", "").replace("google pe search", "").replace("google vr search", "").replace("search for", "").replace("search for", "").strip()
        if not query:
            if lang_code == "hi": return "आप क्या खोजना चाहते हैं?"
            if lang_code == "mr": return "तुम्हाला काय शोधायचे आहे?"
            return "What do you want to search?"
        webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
        if context_state is not None:
            context_state['last_platform'] = 'google'
        if lang_code == "hi": return f"गूगल पर {query} खोजा जा रहा है।"
        if lang_code == "mr": return f"गूगलवर {query} शोधले जात आहे."
        return f"Searching Google for {query}."

    if "google" in cmd and (any(k in cmd for k in ["open", "kholo", "khol", "kru", "skto", "ugha", "ughad", "chalu", "start"]) or cmd == "google"):
        webbrowser.open("https://google.com")
        if context_state is not None:
            context_state['last_platform'] = 'google'
        if lang_code == "hi": return "गूगल खोला जा रहा है, श्रावणी।"
        if lang_code == "mr": return "गूगल सुरू केले जात आहे, श्रावणी."

        return "Opening Google."

    if "instagram" in cmd and (any(k in cmd for k in ["open", "kholo", "khol", "kru", "skto", "ugha", "ughad", "chalu"]) or cmd == "instagram"):
        webbrowser.open("https://instagram.com")
        if lang_code == "hi": return "इंस्टाग्राम खोला जा रहा है।"
        if lang_code == "mr": return "इन्स्टाग्राम सुरू केले जात आहे."
        return "Opening Instagram."
        
    if "whatsapp" in cmd and (any(k in cmd for k in ["web", "open", "kholo", "khol", "kru", "skto", "ugha", "ughad", "chalu"])):
        webbrowser.open("https://web.whatsapp.com")
        if lang_code == "hi": return "व्हाट्सएप वेब खोला जा रहा है।"
        if lang_code == "mr": return "व्हॉट्सअ‍ॅप वेब सुरू केले जात आहे."
        return "Opening WhatsApp Web."
        
    # CONTEXT UNDERSTANDING
    if cmd.startswith("search ") and context_state is not None:
        last = context_state.get('last_platform')
        query = cmd.replace("search", "").strip()
        if last == 'youtube':
            webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
            return f"Searching YouTube for {query}."
        elif last == 'google':
            webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
            return f"Searching Google for {query}."

    return None
