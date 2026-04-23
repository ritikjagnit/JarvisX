import sys
import json
import threading
import time
from voice_engine import speak, is_jarvis_speaking

try:
    import vosk
    import pyaudio
except ImportError:
    vosk = None
    pyaudio = None

class VoiceListenerVosk:
    """
    Real-time robust OFFLINE speech recognition using Vosk.
    Processes audio stream continuously to yield instant results (1-2 sec latency).
    """
    def __init__(self, command_callback, wake_word="jarvis", model_path="model"):
        self.command_callback = command_callback
        self.wake_word = wake_word.lower() if wake_word else None
        self.is_listening = False
        self.model_path = model_path
        
        # Check if modules are installed
        if not vosk or not pyaudio:
            print("[ERROR] Vosk or PyAudio missing. Run: pip install vosk pyaudio")

    def start_listening(self):
        if not vosk or not pyaudio:
            print("[DEBUG] Vosk/PyAudio not available.")
            return

        try:
            print("[DEBUG] Loading Vosk model... this might take a second.")
            # Set log level to -1 to suppress standard vosk spam
            vosk.SetLogLevel(-1) 
            model = vosk.Model(self.model_path)
            # Kaldi Recognizer handles streaming audio effectively
            recognizer = vosk.KaldiRecognizer(model, 16000)
            print("[DEBUG] Vosk model loaded successfully!")
        except Exception as e:
            print(f"[ERROR] Could not load Vosk model at '{self.model_path}': {e}")
            print("Action required:")
            print("1. Download model from https://alphacephei.com/vosk/models (e.g. vosk-model-small-en-us-0.15)")
            print("2. Extract and rename folder to 'model' inside the jarvis_py directory.")
            return

        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, 
                            channels=1, 
                            rate=16000, 
                            input=True, 
                            frames_per_buffer=4000)
            stream.start_stream()
        except Exception as e:
            print(f"[ERROR] PyAudio Audio Stream Failed: {e}")
            return

        self.is_listening = True
        print(f"[DEBUG] VOSK Offline Continuous listening online. Wake word: '{self.wake_word}'")
        speak("Offline voice processing systems initialized.")

        # CONTINUOUS LISTENING LOOP
        while self.is_listening:
            try:
                # Read chunks rapidly (e.g., 4000 frames)
                data = stream.read(4000, exception_on_overflow=False)
                
                # recognizer.AcceptWaveform returns True if silence is detected after speech (phrase boundary)
                if recognizer.AcceptWaveform(data):
                    result_json = recognizer.Result()
                    text = json.loads(result_json).get('text', '').lower()
                    
                    # BLOCK SELF-HEARING
                    if is_jarvis_speaking():
                        # Clear recognized text if Jarvis is the one who spoke it
                        text = ""

                    if text:
                        print(f"[VOSK] Heard: '{text}'")

                        if self.wake_word:
                            if self.wake_word in text:
                                command = text.replace(self.wake_word, "").strip()
                                if not command:
                                    speak("Yes boss?")
                                    continue
                            else:
                                # Not waking, ignore completely
                                continue
                        else:
                            # Without a wake word, any text is a command
                            command = text.strip()

                        if command:
                            print(f"[DEBUG] Instantly routing off-thread: '{command}'")
                            # Run without blocking the ultra-fast audio stream
                            threading.Thread(target=self.command_callback, args=(command,), daemon=True).start()
                else:
                    # Partial result logic can go here for ultra-fast "live" transcription UI rendering
                    # partial_json = recognizer.PartialResult()
                    pass
                    
            except Exception as e:
                print(f"[VOSK] Stream Error: {e}")
                time.sleep(0.5)

        # Cleanup process
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("[DEBUG] Vosk listener gracefully offline.")

    def stop_listening(self):
        self.is_listening = False
        print("[DEBUG] Stop signal sent to Vosk.")
