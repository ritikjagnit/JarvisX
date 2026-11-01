import os
import sys
import time
import subprocess
from voice_engine import speak

try:
    import pyautogui
    pyautogui.PAUSE = 0.1
    pyautogui.FAILSAFE = False
except ImportError:
    pyautogui = None

class WhatsAppAutomation:
    """
    Complete Human-Style WhatsApp Desktop Automation Suite:
    - Search & Open Contact / Group Chat
    - Send Voice Transcribed Messages
    - WhatsApp Voice Call & Video Call
    - Attach Photos / Files / Documents
    - Next / Previous Chat Navigation & Chat Scrolling
    - Search In Chat & Status View
    """
    def __init__(self):
        pass

    def ensure_whatsapp_open(self):
        """Brings WhatsApp Desktop to foreground or launches it via URI protocol."""
        print("[WHATSAPP AUTO] Ensuring WhatsApp Desktop is active...")
        try:
            subprocess.Popen("cmd /c start whatsapp:", shell=True)
            time.sleep(1.5)
            
            if pyautogui:
                width, height = pyautogui.size()
                pyautogui.click(width // 2, height // 2)
            return True
        except Exception as e:
            print(f"[WHATSAPP AUTO ERROR] Could not open WhatsApp: {e}")
            return False

    def open_contact_chat(self, contact_name):
        """
        Searches for contact or group in WhatsApp Desktop and opens chat.
        """
        if not pyautogui:
            return "PyAutoGUI is required for WhatsApp automation."

        self.ensure_whatsapp_open()
        time.sleep(0.8)

        print(f"[WHATSAPP AUTO] Searching for contact/group: '{contact_name}'")
        
        # 1. Clear & Focus Search Box (Ctrl + F)
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.4)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        time.sleep(0.3)

        # 2. Type Contact Name
        pyautogui.typewrite(contact_name, interval=0.04)
        time.sleep(1.8) # Allow WhatsApp search results time to update

        # 3. Select top match contact and open chat
        pyautogui.press('down')
        time.sleep(0.2)
        pyautogui.press('enter')
        time.sleep(0.5)
        pyautogui.press('enter') # Double enter ensures chat is open and active
        time.sleep(0.5)

        return f"Opened chat for '{contact_name}' on WhatsApp."

    def type_message_text(self, message_text):
        """Types transcribed voice text into the active chat input box."""
        if not pyautogui:
            return "PyAutoGUI is required."

        print(f"[WHATSAPP AUTO] Typing message text: '{message_text}'")
        pyautogui.typewrite(message_text + " ", interval=0.02)
        return f"Typed message: '{message_text}'"

    def send_current_message(self):
        """Presses Enter to send the current message in WhatsApp chat."""
        if not pyautogui:
            return "PyAutoGUI is required."

        print("[WHATSAPP AUTO] Pressing Enter to send message...")
        pyautogui.press('enter')
        return "Message sent successfully on WhatsApp!"

    def send_voice_message_to_contact(self, contact_name, message_text=None):
        """Complete workflow: Open Chat -> Type Message -> Send."""
        if not contact_name:
            return "Please specify a contact name."

        res_open = self.open_contact_chat(contact_name)

        if message_text:
            time.sleep(0.5)
            self.type_message_text(message_text)
            time.sleep(0.3)
            self.send_current_message()
            return f"Successfully sent message to '{contact_name}': '{message_text}'"
        else:
            return f"Opened chat with '{contact_name}'. Speak your message and say 'send' to deliver!"

    def make_voice_call(self, contact_name):
        """Initiates WhatsApp Voice Call to specified contact."""
        if not pyautogui:
            return "PyAutoGUI is required."

        self.open_contact_chat(contact_name)
        time.sleep(1.2)

        print(f"[WHATSAPP AUTO] Triggering Voice Call for '{contact_name}'...")
        width, height = pyautogui.size()

        # 1. Primary Keyboard Shortcuts
        pyautogui.hotkey('ctrl', 'shift', 'c')
        time.sleep(0.2)
        pyautogui.hotkey('alt', 'c')
        time.sleep(0.2)

        # 2. Multi-point Header Click Grid across top-right header where Phone Call Icon resides
        for x_ratio in [0.88, 0.91, 0.94, 0.96]:
            for y_pos in [55, 65, 75]:
                pyautogui.click(int(width * x_ratio), y_pos)
                time.sleep(0.05)

        return f"Initiating WhatsApp Voice Call to '{contact_name}'..."

    def make_video_call(self, contact_name):
        """Initiates WhatsApp Video Call to specified contact."""
        if not pyautogui:
            return "PyAutoGUI is required."

        self.open_contact_chat(contact_name)
        time.sleep(1.2)

        print(f"[WHATSAPP AUTO] Triggering Video Call for '{contact_name}'...")
        width, height = pyautogui.size()

        # 1. Primary Keyboard Shortcuts
        pyautogui.hotkey('ctrl', 'shift', 'v')
        time.sleep(0.2)
        pyautogui.hotkey('alt', 'v')
        time.sleep(0.2)

        # 2. Multi-point Header Click Grid across top-right header where Camera Video Icon resides
        for x_ratio in [0.78, 0.81, 0.84, 0.87]:
            for y_pos in [55, 65, 75]:
                pyautogui.click(int(width * x_ratio), y_pos)
                time.sleep(0.05)

        return f"Initiating WhatsApp Video Call to '{contact_name}'..."

    def attach_and_send_file(self, contact_name, file_path=None):
        """Triggers attachment menu in WhatsApp to send photos or documents."""
        if not pyautogui:
            return "PyAutoGUI is required."

        if contact_name:
            self.open_contact_chat(contact_name)
            time.sleep(0.5)

        print("[WHATSAPP AUTO] Opening attachment menu (Ctrl + Shift + U)...")
        pyautogui.hotkey('ctrl', 'shift', 'u')
        return f"Attachment menu opened for '{contact_name}'. Select file to send!"

    def navigate_chats(self, action_type):
        """Navigates next/previous chats or scrolls chat list."""
        if not pyautogui:
            return "PyAutoGUI is required."

        if action_type == "next":
            pyautogui.hotkey('ctrl', 'tab')
            return "Switched to next chat."
        elif action_type == "previous":
            pyautogui.hotkey('ctrl', 'shift', 'tab')
            return "Switched to previous chat."
        elif action_type == "scroll_down":
            pyautogui.press('pagedown')
            return "Scrolled chat list down."
        elif action_type == "scroll_up":
            pyautogui.press('pageup')
            return "Scrolled chat list up."
        return "Navigated chats."

# Singleton instance
whatsapp_auto = WhatsAppAutomation()

def clean_contact_name(text):
    """
    Strips action keywords, Hinglish fillers, and extra words to extract clean contact name.
    Example: 'noman ko call kro' -> 'Noman'
    """
    fillers = [
        "whatsapp video call to", "whatsapp voice call to", "whatsapp call to",
        "video call to", "voice call to", "whatsapp video call", "whatsapp voice call",
        "whatsapp call", "video call", "voice call", "call to", "call",
        "ko video call karo", "ko voice call karo", "ko call karo", "ko call kar do", "ko call kro", "ko call krdo",
        "video call karo", "voice call karo", "call karo", "call kar do", "call kro", "call krdo",
        "whatsapp pe call karo", "whatsapp pe call", "whatsapp par call", "pe call karo", "par call karo",
        "pe call", "par call", "whatsapp pe", "whatsapp par",
        "ko message bhejo", "ko msg bhejo", "ko message kar do", "message to",
        "send message to", "send whatsapp to", "send photo to", "send file to",
        "open chat for", "open chat with", "open chat", "chat with",
        "ko", "karo", "kar do", "kro", "krdo", "bhejo", "kholo", "open", "pe", "par"
    ]
    cleaned = text.lower()
    for filler in fillers:
        cleaned = cleaned.replace(filler, " ")
    
    stop_words = {"ko", "karo", "kro", "krdo", "call", "whatsapp", "video", "voice", "bhejo", "msg", "message", "send", "to", "namaste"}
    words = [w for w in cleaned.split() if w not in stop_words]
    if not words:
        return ""
    
    return " ".join([w.capitalize() for w in words])

def process_whatsapp_command(command):
    """
    Full Human-Style WhatsApp Voice Intent Router:
    - Text Messaging: 'send message to Rahul: Hi bro', 'Rahul ko message bhejo'
    - Voice Calls: 'call Rahul on whatsapp', 'voice call Rahul', 'Rahul ko call karo'
    - Video Calls: 'video call Priya', 'Priya ko video call karo'
    - Open Chat/Group: 'open chat Rahul', 'open group College Friends'
    - File Attachments: 'send photo to Rahul', 'attach file'
    - Navigation: 'next chat', 'previous chat', 'scroll chat'
    - Confirm Send: 'send', 'bhej do'
    """
    cmd = command.lower().strip()

    # 1. Video Call Intent (Checked BEFORE voice call to avoid mis-matching)
    if any(k in cmd for k in ["video call", "whatsapp video call"]):
        contact_name = clean_contact_name(cmd)
        if contact_name:
            return whatsapp_auto.make_video_call(contact_name)
        else:
            return "Whom would you like to video call on WhatsApp, Shravani?"

    # 2. Voice Call Intent
    if any(k in cmd for k in ["voice call", "call on whatsapp", "whatsapp call", "call karo", "call kar do", "call kro", "call krdo"]) or ("call" in cmd and "message" not in cmd):
        contact_name = clean_contact_name(cmd)
        if contact_name:
            return whatsapp_auto.make_voice_call(contact_name)
        else:
            return "Whom would you like to call on WhatsApp, Shravani?"


    # 3. File & Photo Attachment Intent
    if any(k in cmd for k in ["send photo", "send file", "send document", "attach file", "photo bhejo"]):
        contact_name = clean_contact_name(cmd)
        return whatsapp_auto.attach_and_send_file(contact_name)

    # 4. Chat Navigation Intent
    if cmd in ["next chat", "agla chat"]:
        return whatsapp_auto.navigate_chats("next")
    if cmd in ["previous chat", "purana chat", "back chat"]:
        return whatsapp_auto.navigate_chats("previous")
    if cmd in ["scroll chat down", "scroll chats", "niche karo"]:
        return whatsapp_auto.navigate_chats("scroll_down")

    # 5. Direct Text Messaging Intent: "send message to [name]: [text]" or "[name] ko message [text]"
    if any(k in cmd for k in ["message to", "send message to", "send whatsapp to", "ko message", "ko msg"]):
        clean_cmd = cmd.replace("send whatsapp message to", "").replace("send whatsapp to", "").replace("send message to", "").replace("message to", "").strip()
        
        contact_name = ""
        message_text = ""

        if ":" in clean_cmd:
            parts = clean_cmd.split(":", 1)
            contact_name = parts[0].strip()
            message_text = parts[1].strip()
        elif " ko message " in cmd or " ko msg " in cmd:
            if " ko message " in cmd:
                parts = cmd.split(" ko message ", 1)
            else:
                parts = cmd.split(" ko msg ", 1)
            contact_name = parts[0].replace("send ", "").replace("whatsapp ", "").strip()
            message_text = parts[1].strip()
        else:
            words = clean_cmd.split()
            if len(words) >= 2:
                contact_name = words[0]
                message_text = " ".join(words[1:])
            elif len(words) == 1:
                contact_name = words[0]

        if contact_name and message_text:
            return whatsapp_auto.send_voice_message_to_contact(contact_name, message_text)
        elif contact_name:
            return whatsapp_auto.open_contact_chat(contact_name)

    # 6. Open Contact / Group Chat Intent: "open chat Rahul", "open group College"
    if any(k in cmd for k in ["open chat", "whatsapp chat", "chat with", "open group"]):
        contact_name = cmd.replace("open group", "").replace("open chat for", "").replace("open chat with", "").replace("open chat", "").replace("whatsapp chat", "").replace("chat with", "").replace("kholo", "").strip()
        if contact_name:
            return whatsapp_auto.open_contact_chat(contact_name)

    # 7. Confirm Send Command: "send" / "send it" / "bhej do"
    if cmd in ["send", "send it", "bhej do", "send message", "message bhej do", "press send"]:
        return whatsapp_auto.send_current_message()

    return None
