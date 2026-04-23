from voice_listener import VoiceListener
from command_router import CommandRouter

def start_assistant():
    print("===========================================")
    print(" Jarvis Multitasking AI - Always On Edition")
    print("===========================================")
    
    # 1. Initialize Brain System (Router)
    brain = CommandRouter()
    
    # 2. Initialize Always-On Ear System (Listener)
    # The listener continuously loops. Whenever speech is heard, it sends
    # the processed text straight to brain.route
    ear = VoiceListener(command_callback=brain.route, wake_word="jarvis")
    
    print("\nSYSTEM: Starting continuous loop...")
    print("HINT: Try saying 'Jarvis open calculator', then immediately 'Jarvis close calculator'")
    
    # 3. Enter real-time synchronous blocking loop
    try:
        ear.start_listening()
    except KeyboardInterrupt:
        print("\nManual Override. Shutting down Jarvis.")
        ear.stop_listening()

if __name__ == "__main__":
    start_assistant()
