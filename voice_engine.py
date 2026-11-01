import subprocess
import sys
import os
import json
import time
import ctypes
import threading
import queue

# Removed Google SpeechRecognition as per strict offline requirement
VOICE_INPUT_AVAILABLE = True # Controlled by Vosk now

# GLOBAL STATE to prevent self-hearing and control overlapping
is_speaking_now = False
is_ultron_voice_mode = False
is_stark_voice_mode = True # Default Tony Stark British Butler Voice
speech_queue = queue.Queue()

def set_ultron_voice_mode(enabled: bool):
    global is_ultron_voice_mode
    is_ultron_voice_mode = bool(enabled)
    print(f"[VOICE ENGINE] Ultron Voice Mode set to: {is_ultron_voice_mode}")

def set_stark_voice_mode(enabled: bool):
    global is_stark_voice_mode
    is_stark_voice_mode = bool(enabled)
    print(f"[VOICE ENGINE] Stark Protocol British Voice Mode set to: {is_stark_voice_mode}")

def run_async(coro):
    import asyncio
    import concurrent.futures
    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop_policy().get_event_loop()
    except Exception:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    if loop.is_running():
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    else:
        return loop.run_until_complete(coro)

def is_internet_connected():
    import socket
    try:
        socket.setdefaulttimeout(1.5)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        return True
    except Exception:
        return False

import re

def clean_text_for_speech(text):
    if not text:
        return ""

    # Remove Markdown headers, bold, italics, code blocks
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'\*+([^*]+)\*+', r'\1', text)
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'[•\-\*]', '', text)

    # Normalize technical acronyms for clear Indian TTS pronunciation
    acronym_map = {
        r'\bAI\b': 'A.I.',
        r'\bVS Code\b': 'V.S. Code',
        r'\bPDF\b': 'P.D.F.',
        r'\bOCR\b': 'O.C.R.',
        r'\bCPU\b': 'C.P.U.',
        r'\bRAM\b': 'R.A.M.',
        r'\bGPU\b': 'G.P.U.',
        r'\bSHRIVA AI\b': 'Shriva A.I.',
        r'\bGB\b': 'G.B.',
        r'\bMB\b': 'M.B.',
        r'\bQR\b': 'Q.R.',
        r'\bOTP\b': 'O.T.P.',
        r'\bUI\b': 'U.I.',
        r'\bPC\b': 'P.C.',
        r'\bATS\b': 'A.T.S.',
        r'\bTTS\b': 'T.T.S.'
    }
    for pattern, replacement in acronym_map.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Clean multiple spaces and linebreaks
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def speak_neural(text, voice_index, lang_code="en"):
    if not is_internet_connected():
        raise RuntimeError("No Internet Connection")

    import edge_tts
    
    clean_text = clean_text_for_speech(text)
    if not clean_text:
        return True

    global is_ultron_voice_mode, is_stark_voice_mode
    pitch = "+0Hz"
    rate = "+8%"

    if is_ultron_voice_mode:
        voice = "en-US-ChristopherNeural"
        pitch = "-25Hz"
        rate = "-5%"
    elif is_stark_voice_mode:
        # Authentic Paul Bettany British JARVIS voice
        voice = "en-GB-RyanNeural"
        pitch = "+0Hz"
        rate = "+5%"
    else:
        # 100% Pure English (Indian Accent)
        voice = "en-IN-NeerjaNeural" if voice_index == 1 else "en-IN-PrabhatNeural"
        
    temp_dir = "jarvis_data"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    filepath = os.path.join(temp_dir, f"speech_{time.time_ns()}.mp3")
    abspath = os.path.abspath(filepath)
    
    async def save_speech():
        communicate = edge_tts.Communicate(clean_text, voice, pitch=pitch, rate=rate)
        await communicate.save(abspath)
        
    run_async(save_speech())
    
    if not os.path.exists(abspath) or os.path.getsize(abspath) == 0:
        raise RuntimeError("Neural TTS audio generation empty")

    global is_speaking_now
    is_speaking_now = True

    alias = f"mp3_{time.time_ns()}"
    try:
        open_cmd = f'open "{abspath}" type mpegvideo alias {alias}'
        ctypes.windll.winmm.mciSendStringW(open_cmd, None, 0, 0)
        
        play_cmd = f'play {alias}'
        ctypes.windll.winmm.mciSendStringW(play_cmd, None, 0, 0)

        def _async_cleanup():
            global is_speaking_now
            is_speaking_now = True
            est_duration = max(2.5, len(clean_text) * 0.075) + 0.5
            time.sleep(est_duration)
            close_cmd = f'close {alias}'
            ctypes.windll.winmm.mciSendStringW(close_cmd, None, 0, 0)
            if os.path.exists(abspath):
                try:
                    os.remove(abspath)
                except Exception:
                    pass
            is_speaking_now = False

        threading.Thread(target=_async_cleanup, daemon=True).start()
    except Exception as ex:
        print(f"[AUDIO PLAYBACK NOTICE] {ex}")
        is_speaking_now = False
    return True


def _speak_worker(text, voice_index, lang_code="en"):
    global is_speaking_now
    is_speaking_now = True
    
    # 1. Primary: Hyper-Realistic Human HD Neural Voice (Crystal Clear Pronunciation)
    try:
        if speak_neural(text, voice_index, lang_code=lang_code):
            return
    except Exception as e:
        print(f"[VOICE NOTICE] Neural HD Voice unavailable ({e}), using offline SAPI5 fallback.")

    # 2. Offline Fallback (used when internet is disconnected)
    sapi_spoken = False
    try:
        import pyttsx3
        import pythoncom
        pythoncom.CoInitialize()
        engine = pyttsx3.init()
        engine.setProperty("rate", 175)
        engine.setProperty("volume", 1.0)
        voices = engine.getProperty("voices")
        if voices and voice_index < len(voices):
            engine.setProperty("voice", voices[voice_index].id)
        
        engine.say(text)
        engine.runAndWait()
        del engine
        sapi_spoken = True
    except Exception:
        pass

    if not sapi_spoken:
        try:
            # Native Windows SAPI5 (100% built into Windows OS, zero dependencies)
            clean_s = text.replace('"', ' ').replace("'", " ")[:300]
            cmd = f'powershell -WindowStyle Hidden -Command "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{clean_s}\')"'
            subprocess.run(cmd, shell=True, timeout=12)
        except Exception:
            pass

    is_speaking_now = False


def _queue_processor():
    while True:
        try:
            item = speech_queue.get()
            if len(item) == 3:
                text, voice_index, lang_code = item
            else:
                text, voice_index = item
                lang_code = "en"
            _speak_worker(text, voice_index, lang_code=lang_code)
            speech_queue.task_done()
        except Exception as e:
            print(f"[VOICE QUEUE PROCESSOR ERROR] {e}")


# Start global background thread to process speech queue sequentially
queue_thread = threading.Thread(target=_queue_processor, daemon=True)
queue_thread.start()


def speak(text, async_play=True):
    if not text:
        return

    voice_index = 0
    lang_code = "en"
    settings_path = os.path.join("jarvis_data", "voice_settings.json")
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r") as f:
                data = json.load(f)
                voice_index = data.get("voice_index", 0)
                lang_code = data.get("language", "en")
        except Exception:
            voice_index = 0
            lang_code = "en"

    if async_play:
        speech_queue.put((text, voice_index, lang_code))
    else:
        # Wait for the queue to clear and speak synchronously
        while not speech_queue.empty():
            time.sleep(0.1)
        _speak_worker(text, voice_index, lang_code=lang_code)


def is_jarvis_speaking():
    return is_speaking_now or not speech_queue.empty()

def listen():
    """ 
    Legacy fallback listener is removed. 
    Vosk engine handles continuous streaming completely. 
    """
    print("[DEBUG] Fallback listener disabled in favor of offline Vosk streaming.")
    return ""