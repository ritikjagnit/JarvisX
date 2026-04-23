import datetime
import os
import subprocess
import webbrowser
import time
from urllib.parse import quote_plus

import requests

try:
    import pyautogui
except ImportError:
    pyautogui = None

from voice_engine import speak, listen
from plugins.jokes import tell_joke
from plugins.weather import get_weather
from plugins.image_generator import process_image_command
from plugins.letter_generator import generate_letter
try:
    from api_keys import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = ""


# ---------------- OLLAMA ----------------

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

pending_action = None


# ---------------- RESPONSE ----------------

def respond(msg):
    # Strictly return message for central handler, do NOT speak here directly.
    return msg


# ---------------- AI ----------------

def ask_ai(prompt):
    """ Tries local Ollama first, then falls back to OpenAI if available. """
    try:
        # 1. TRY OLLAMA (Local)
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": f"Answer short and clear: {prompt}",
                "stream": False
            },
            timeout=3 # Fast fail for local
        )
        return respond(response.json().get("response", "No response"))
    except:
        # 2. FALLBACK TO OPENAI (Online)
        if OPENAI_API_KEY:
            try:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
                data = {
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "system", "content": "You are Jarvis, a helpful AI."}, {"role": "user", "content": prompt}]
                }
                res = requests.post(url, headers=headers, json=data, timeout=5)
                return respond(res.json()["choices"][0]["message"]["content"])
            except:
                return respond("Ollama is offline and OpenAI failed. Check internet.")
        
        return respond("AI is not available right now (Ollama offline).")




import requests
import subprocess
import time
import os

API_KEY = OPENAI_API_KEY

def write_letter(prompt):
    respond("Writing your document...")

    try:
        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a professional letter writer."},
                {"role": "user", "content": f"Write a professional letter for: {prompt}. Only output the letter."}
            ]
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code != 200:
            return respond("AI error. Check API key or internet.")

        result = response.json()
        content = result["choices"][0]["message"]["content"]

        # Save in Documents
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        filename = os.path.join(documents_path, f"letter_{int(time.time())}.txt")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

        subprocess.Popen(["notepad.exe", filename])

        return respond("Your document is ready and opened.")

    except Exception as e:
        print("ERROR:", e)
        return respond("Something went wrong.")


# ---------------- SYSTEM ----------------

def confirm_shutdown():
    global pending_action
    pending_action = "shutdown"
    return respond("Are you sure you want to shutdown?")


def confirm_restart():
    global pending_action
    pending_action = "restart"
    return respond("Are you sure you want to restart?")


def execute_pending(action):
    global pending_action
    pending_action = None

    if action == "shutdown":
        os.system("shutdown /s /t 5")
        return respond("Shutting down system")

    if action == "restart":
        os.system("shutdown /r /t 5")
        return respond("Restarting system")


# ---------------- APPS ----------------

apps = {
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "notepad": "notepad"
}

app_process = {
    "chrome": "chrome.exe",
    "notepad": "notepad.exe"
}


def open_app(app):
    subprocess.Popen(apps[app])
    return respond(f"Opening {app}")


def close_app(app):
    os.system(f"taskkill /f /im {app_process[app]}")
    return respond(f"Closing {app}")


# ---------------- WEB ----------------

def open_website(url):
    webbrowser.open(url)
    return respond("Opening website")


def search_google(query):
    webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
    return respond(f"Searching Google for {query}")


def search_youtube(query):
    webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
    return respond(f"Searching YouTube for {query}")


def play_on_spotify(query):
    webbrowser.open(f"https://open.spotify.com/search/{quote_plus(query)}")
    return respond(f"Playing {query} on Spotify")


# ---------------- WHATSAPP ----------------

def open_whatsapp():
    webbrowser.open("https://web.whatsapp.com")
    time.sleep(10)
    return respond("WhatsApp is ready")


def send_message_whatsapp(name, message):

    if pyautogui is None:
        return respond("PyAutoGUI not installed")

    try:
        # click search box (adjust if needed)
        pyautogui.click(x=200, y=200)
        time.sleep(1)

        pyautogui.hotkey("ctrl", "a")
        pyautogui.press("backspace")

        pyautogui.write(name)
        time.sleep(2)

        pyautogui.press("enter")
        time.sleep(2)

        pyautogui.write(message)
        pyautogui.press("enter")

        return respond(f"Message sent to {name}")

    except Exception as e:
        print("WHATSAPP ERROR:", e)
        return respond("Failed to send message")


# ---------------- UTIL ----------------

def get_time():
    return respond(datetime.datetime.now().strftime("Time is %H:%M"))


def screenshot():
    if pyautogui:
        pyautogui.screenshot().save("screenshot.png")
    return respond("Screenshot taken")


# ---------------- COMMAND ENGINE ----------------

def process_command(command):

    global pending_action

    cmd = command.lower().strip()
    print("User:", cmd)

    # CONFIRMATION
    if pending_action:
        if "yes" in cmd:
            return execute_pending(pending_action)
        if "no" in cmd:
            pending_action = None
            return respond("Cancelled")

    # SYSTEM
    if "shutdown" in cmd:
        return confirm_shutdown()

    if "restart" in cmd:
        return confirm_restart()

    # APPS
    if "open chrome" in cmd:
        return open_app("chrome")

    if "close chrome" in cmd:
        return close_app("chrome")

    if "open notepad" in cmd:
        return open_app("notepad")

    # DOCUMENTS
    # Call new local letter generator for specific types
    if "write" in cmd and "letter" in cmd and any(t in cmd for t in ["love", "leave", "holiday"]):
        generate_letter(cmd)
        return respond("Letter typed successfully.")

    # Fallback to online AI letter generation
    if any(keyword in cmd for keyword in ["letter", "application"]) and any(verb in cmd for verb in ["write", "generate", "create", "likho", "type"]):
        return write_letter(cmd)

    # WHATSAPP
    if "open whatsapp" in cmd:
        return open_whatsapp()

    if "send message to" in cmd:

        name = cmd.split("send message to")[1].strip()

        respond(f"What message should I send to {name}?")

        message = listen()

        if not message:
            return respond("I didn't hear the message")

        return send_message_whatsapp(name, message)

    # WEBSITES
    if cmd.startswith("open youtube"):
        return open_website("https://youtube.com")

    if cmd.startswith("open google"):
        return open_website("https://google.com")

    # PLAY
    if cmd.startswith("play "):
        query = cmd.replace("play ", "").strip()
        if any(x in cmd for x in ["song", "music", "spotify"]):
            return play_on_spotify(query)
        if query:
            return search_youtube(query)

    # SEARCH
    if cmd.startswith("search youtube "):
        query = cmd.replace("search youtube ", "").strip()
        if query:
            return search_youtube(query)

    if cmd.startswith("search "):
        query = cmd.replace("search ", "").strip()
        if query:
            return search_google(query)

    # UTIL
    if "time" in cmd:
        return get_time()

    if "screenshot" in cmd:
        return screenshot()

    # PLUGINS
    if "joke" in cmd:
        return respond(tell_joke())

    if "weather" in cmd:
        return respond(get_weather())

    if "generate" in cmd and "image" in cmd:
        return process_image_command(cmd)
    
    if "banana" in cmd and "image" in cmd: # Just in case
        return process_image_command(cmd)

    # EXIT
    if "stop jarvis" in cmd:
        return respond("Stopping Jarvis")

    # AI Fallback removed for flexible central routing
    return None