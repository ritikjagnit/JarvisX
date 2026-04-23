import threading
from voice_engine import speak
# Legacy imports
from command_engine import process_command as old_process_command, ask_ai

# English-only modular inputs
from open_app import open_app
from close_app import close_app
from memory import process_memory_command
from notes import process_notes_command
from conversation import process_conversation
from file_manager import process_file_command
from browser_control import process_browser_command
from advanced_system import process_system_command
from jarvis_utilities import JarvisUtilities
from plugins.image_generator import process_image_command
from plugins.code_generator import process_code_command

class CommandRouter:
    """
    MODULAR BRAIN SYSTEM:
    Routes intents rapidly, acts completely offline, features state tracking natively, 
    and outputs securely to voice + text. No Hindi wrappers!
    """
    def __init__(self, ui_callback=None):
        self.ui_callback = ui_callback
        
        # State Management System
        self.context_state = {
            "last_platform": None,
            "pending_memory": None, # Holds temporary memory dicts
            "last_command": None
        }
        self.utilities = JarvisUtilities()
        print("[DEBUG] Command Router (Brain) Successfully Initialized.")

    def route(self, command):
        if not command: return None
        
        # English normalization & Logging
        command = command.lower().strip()
        self.context_state["last_command"] = command
        
        print(f"\n[ROUTER] Dispatching command: '{command}'")
        
        # Run synchronously. Threading is now natively handled securely by the command_worker queue.
        return self._execute_intent(command)

    def _execute_intent(self, command):
        try:
            response = None
            
            # Module Routing (Descending Priority)
            # 1. State Tracking (Memory Confirmation Prompt explicitly handles context)
            response = process_memory_command(command, self.context_state)
            
            # 2. General Tool Routing
            if not response: response = process_system_command(command)
            if not response: response = process_conversation(command)
            if not response: response = process_notes_command(command)
            if not response: response = process_file_command(command)
            if not response: response = process_browser_command(command, self.context_state)
            if not response: response = process_code_command(command)
            if not response: response = process_image_command(command)
            
            # 3. Utilities (Math, Time, Conversions, System Status)
            if not response:
                response = self.utilities.process_utility_command(command)

            # Return structure!
            if response:
                print(f"[ROUTER] Output generated: {response}")
                return response

            # Keep Close application Intent
            if command.startswith("close "):
                app_name = command.replace("close ", "").strip()
                if app_name:
                    success = close_app(app_name)
                    if success:
                        self.context_state['last_platform'] = None
                    return f"Terminating {app_name}." if success else f"I couldn't find {app_name} running."
                return "Which application should I close?"

            # Open application Intent
            if command.startswith("open "):
                app_name = command.replace("open ", "").strip()
                # Bypass fallbacks if caught dynamically (handled by browser module)
                if app_name not in ["google", "whatsapp", "youtube", "instagram"]:
                    success = open_app(app_name)
                    if success: 
                        self.context_state['last_platform'] = None
                        return f"Operating {app_name}."
                    return f"Sorry, I couldn't find {app_name} on your system."

            # 4. LEGACY FALLBACK API ROUTING (Tool fallbacks like Jokes, Weather)
            response = old_process_command(command)
            if response:
                print(f"[ROUTER] Legacy Output generated: {response}")
                return response

            # 5. FINAL AI FALLBACK (Ollama / Local Brain)
            # This is now reached if no other tool or contextual command matched.
            return ask_ai(command)
                
        except Exception as e:
            err_msg = "I encountered an error executing that command."
            print(f"[ROUTER] CRITICAL ERROR on '{command}': {e}")
            return err_msg
