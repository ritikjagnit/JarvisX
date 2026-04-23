import time
import threading
from voice_engine import speak, VOICE_INPUT_AVAILABLE, is_jarvis_speaking
try:
    import speech_recognition as sr
except ImportError:
    sr = None

class VoiceListener:
    def __init__(self, command_callback, wake_word="jarvis"):
        self.command_callback = command_callback
        self.wake_word = wake_word.lower() if wake_word else None
        self.recognizer = sr.Recognizer() if VOICE_INPUT_AVAILABLE else None
        self.is_listening = False

    def start_listening(self):
        if not self.recognizer:
            print("[DEBUG] Voice input not available. Microphone/SpeechRecognition missing.")
            return

        self.is_listening = True
        print(f"[DEBUG] Continuous listening online. Wake word: '{self.wake_word}'")

        # IMPROVE SPEECH RECOGNITION SPEED
        self.recognizer.pause_threshold = 0.5
        self.recognizer.non_speaking_duration = 0.4

        with sr.Microphone() as source:
            print("[DEBUG] Adjusting to background noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            speak("I am now online and listening continuously.")

        # CONTINUOUS LISTENING (CRITICAL)
        while self.is_listening:
            # BLOCK LISTENING WHILE SPEAKING (Early check)
            if is_jarvis_speaking():
                time.sleep(0.3)
                continue

            try:
                with sr.Microphone() as source:
                    # Decrease timeout to reduce waits
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                
                # Double check to prevent processing what was just captured if speak() started mid-listen
                if is_jarvis_speaking():
                    continue

                command = self.recognizer.recognize_google(audio).lower()
                
                if command:
                    print(f"[VOICE] Heard: {command}")

                if self.wake_word and self.wake_word in command:
                    command = command.replace(self.wake_word, "").strip()
                    if not command:
                        speak("Yes boss?")
                        continue

                if command:
                    print(f"[DEBUG] Delegating '{command}' to Main Command Queue...")
                    self.command_callback(command, source="voice")

            # FIX 5: ERROR HANDLING
            except sr.WaitTimeoutError:
                # Expected timeout when user is silent, loop keeps running
                continue
            except sr.UnknownValueError:
                print("[VOICE] Recognition Error: Could not understand audio.")
                continue
            except sr.RequestError as e:
                print(f"[VOICE] API Error: {e}")
                continue
            except Exception as e:
                print(f"[VOICE] Listener system error (Retrying): {e}")
                time.sleep(1) # Grace period before retry to prevent cpu hogging

    def stop_listening(self):
        self.is_listening = False
        print("[DEBUG] Continuous listening manually stopped via system.")
