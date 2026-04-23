import subprocess
import sys

# Removed Google SpeechRecognition as per strict offline requirement
VOICE_INPUT_AVAILABLE = True # Controlled by Vosk now

# GLOBAL STATE to prevent self-hearing
is_speaking_now = False

def speak(text):
    global is_speaking_now
    if not text:
        return

    # Set Flag
    is_speaking_now = True

    # PERSISTENT VOICE SELECTION
    import json
    import os
    voice_index = 0
    settings_path = os.path.join("jarvis_data", "voice_settings.json")
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r") as f:
                voice_index = json.load(f).get("voice_index", 0)
        except:
            voice_index = 0

    script = '''
import sys
import pyttsx3
import pythoncom
try:
    pythoncom.CoInitialize()
    engine = pyttsx3.init()
    
    # OPTIMIZED FOR CLARITY (INDIAN ACCENT COMPATIBILITY)
    engine.setProperty("rate", 145) 
    engine.setProperty("volume", 1.0)
    
    voices = engine.getProperty("voices")
    voice_index = int(sys.argv[2])
    
    if voices:
        target_id = voices[0].id # Fallback
        
        # Smart Indian Voice Detection (if index matching fails)
        if voice_index == 1: # Female Request
             # Try to find a female Indian voice like 'Heera' or 'Zira'
             for v in voices:
                 name = v.name.lower()
                 if ("india" in name or "heera" in name or "zira" in name) and "female" in name:
                     target_id = v.id
                     break
             else:
                 # Fallback to standard female if index 1 is valid
                 target_id = voices[1].id if len(voices) > 1 else voices[0].id
        else: # Male Request
             for v in voices:
                 if ("india" in v.name.lower() or "ravi" in v.name.lower()) and "male" in v.name.lower():
                     target_id = v.id
                     break
             else:
                 target_id = voices[0].id

        engine.setProperty("voice", target_id)
        
    text = sys.argv[1]
    engine.say(text)
    engine.runAndWait()
except Exception as e:
    pass
'''
    try:
        # We use run() instead of Popen() to block the thread while speaking!
        # This prevents the worker from handling new commands until speaking is done,
        # AND it allows us to track the speaking state reliably.
        CREATE_NO_WINDOW = 0x08000000
        subprocess.run([sys.executable, "-c", script, text, str(voice_index)], creationflags=CREATE_NO_WINDOW)
    except Exception as e:
        print(f"[VOICE ERROR] Failed to perform TTS: {e}")
    finally:
        import time
        time.sleep(0.5) # Silence cooldown to avoid echo-hearing
        is_speaking_now = False

def is_jarvis_speaking():
    return is_speaking_now

def listen():
    """ 
    Legacy fallback listener is removed. 
    Vosk engine handles continuous streaming completely. 
    """
    print("[DEBUG] Fallback listener disabled in favor of offline Vosk streaming.")
    return ""