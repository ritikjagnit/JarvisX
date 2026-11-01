import time
import threading
from voice_engine import speak, VOICE_INPUT_AVAILABLE, is_jarvis_speaking
try:
    import speech_recognition as sr
except ImportError:
    sr = None

import re
import os
import json

def correct_phonetic_mishearings(text):
    if not text:
        return ""

    replacements = {
        r'\byou tube\b': 'youtube',
        r'\byu tube\b': 'youtube',
        r'\byutub\b': 'youtube',
        r'\bwhats app\b': 'whatsapp',
        r'\bwhat\'s app\b': 'whatsapp',
        r'\bvatsap\b': 'whatsapp',
        r'\bwatsap\b': 'whatsapp',
        r'\binsta gram\b': 'instagram',
        r'\bgugle\b': 'google',
        r'\bgugol\b': 'google',
        r'\bjanam kundali\b': 'astro profile',
        r'\bjanam kundli\b': 'astro profile',
        r'\bkundli\b': 'astro profile',
        r'\bkundali\b': 'astro profile',
        r'\bpasswords\b': 'cyber vault',
        r'\bpass word\b': 'cyber vault',
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text

class VoiceListener:
    def __init__(self, command_callback, wake_word="intelligent ai"):
        self.command_callback = command_callback
        self.wake_word = wake_word.lower() if wake_word else None
        self.wake_words = ["shriva ai", "shriva", "intelligent ai", "intelligent", "ai assistant", "nexus prime", "nexus", "jarvis"]
        self.recognizer = sr.Recognizer() if VOICE_INPUT_AVAILABLE else None
        self.is_listening = False

    def start_listening(self):
        if not self.recognizer:
            print("[DEBUG] Voice input not available. Microphone/SpeechRecognition missing.")
            return

        self.is_listening = True
        print(f"[DEBUG] Continuous listening online. Wake word: '{self.wake_word}'")

        # HIGH-ACCURACY & ULTRA-SENSITIVE WHISPER SPEECH PARAMETERS
        self.recognizer.pause_threshold = 0.8
        self.recognizer.non_speaking_duration = 0.5
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_ratio = 1.15
        self.recognizer.dynamic_energy_adjustment_damping = 0.15

        try:
            with sr.Microphone() as source:
                print("[DEBUG] Calibrating microphone & background noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
                # Ultra-sensitive whisper threshold (80-120) so user can speak softly without shouting!
                calibrated_floor = self.recognizer.energy_threshold * 0.4
                self.recognizer.energy_threshold = max(80, min(120, calibrated_floor))
                print(f"[DEBUG] Sensitive Whisper Energy Threshold set to: {self.recognizer.energy_threshold:.1f}")
                print("[DEBUG] Continuous microphone listener calibrated silently.")

                # CONTINUOUS LISTENING (HIGH PERFORMANCE)
                while self.is_listening:
                    # BLOCK LISTENING WHILE SPEAKING
                    if is_jarvis_speaking():
                        time.sleep(0.2)
                        continue

                    try:
                        # Listen with comfortable phrase timeout
                        audio = self.recognizer.listen(source, timeout=2.5, phrase_time_limit=8)
                        
                        if is_jarvis_speaking():
                            continue

                        primary_locale = "en-IN"
                        fallback_locale = "en-US"

                        command = ""
                        try:
                            command = self.recognizer.recognize_google(audio, language=primary_locale).lower().strip()
                        except sr.UnknownValueError:
                            try:
                                command = self.recognizer.recognize_google(audio, language=fallback_locale).lower().strip()
                            except Exception:
                                pass

                        command = correct_phonetic_mishearings(command)

                        if command:
                            print(f"[VOICE] Heard: {command}")

                        # Filter out background noise artifacts & self-echo playback phrases
                        noise_fillers = ["i am", "i'm", "i", "me", "am", "a", "an", "the", "is", "are"]
                        echo_phrases = ["how can i help", "how can i help you", "how can i help you today", "i am shriva ai", "your personal ai assistant", "i am intelligent ai", "how can i assist", "i am now online"]
                        
                        if command in noise_fillers or any(ep in command for ep in echo_phrases):
                            print(f"[VOICE IGNORED] Filtered out ambient noise / self-echo artifact: '{command}'")
                            continue

                        wake_found = False
                        for w in getattr(self, 'wake_words', ["shriva ai", "shriva", "nexus prime", "nexus", "jarvis"]):
                            if w in command:
                                command = command.replace(w, "").strip()
                                wake_found = True
                                break
                        
                        if wake_found and not command:
                            speak("Yes Shravani?")
                            continue


                        if command and command not in noise_fillers:
                            print(f"[DEBUG] Delegating '{command}' to Main Command Queue...")
                            self.command_callback(command, source="voice")

                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError as e:
                        print(f"[VOICE] API Error: {e}")
                        continue
                    except Exception as e:
                        print(f"[VOICE] Listener system error (Retrying): {e}")
                        time.sleep(1) # Grace period before retry to prevent cpu hogging
        except Exception as e:
            print(f"[VOICE] Microphone initialization error: {e}")

    def stop_listening(self):
        self.is_listening = False
        print("[DEBUG] Continuous listening manually stopped via system.")
