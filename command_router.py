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
from screenshot_analyzer import process_screenshot_command
from ocr_processor import process_ocr_command
try:
    from excel_automation import process_excel_command
except Exception:
    process_excel_command = lambda cmd: None

try:
    from letter_writer import is_letter_command, process_letter_command
except Exception:
    is_letter_command = lambda cmd: False
    process_letter_command = lambda cmd, ctx=None, cb=None: None


def detect_and_set_language(command):
    return "en"

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
        
        # Auto-detect language dynamically from command
        detect_and_set_language(command)

        # Reset proactive idle timer whenever user gives a command
        try:
            from proactive_companion import update_last_user_activity
            update_last_user_activity()
        except Exception:
            pass

        # English normalization & Logging
        command = command.lower().strip()
        wake_prefixes = ["hey intelligent ai ", "hey intelligent ", "hey jarvis ", "hey nexus ", "intelligent ai ", "nexus prime ", "shriva ai ", "intelligent ", "shriva ", "nexus ", "jarvis "]
        for w in wake_prefixes:
            if command.startswith(w):
                command = command[len(w):].strip()
                break

        if not command or command in ["intelligent ai", "intelligent", "jarvis", "nexus", "nexus prime", "hey intelligent ai", "hey intelligent", "hey jarvis", "hey nexus", "shriva ai", "shriva", "hi", "hello", "hey", "i am", "i'm", "i", "me", "am", "a", "an", "the", "is", "are", "how can i help", "how can i help you", "how can i help you today", "how can i assist"]:
            return "Yes Shravani? I am online and listening. How can I help you?"

        self.context_state["last_command"] = command
        
        print(f"\n[ROUTER] Dispatching command: '{command}'")
        
        # Run synchronously. Threading is now natively handled securely by the command_worker queue.
        return self._execute_intent(command)

    def _execute_intent(self, command):
        try:
            response = None
            
            # Browser & Website Intent Router (Multi-Lingual)
            if any(k in command for k in ["youtube", "google", "instagram", "whatsapp"]):
                res = process_browser_command(command, self.context_state)
                if res:
                    return res

            # AI Letter Writer & Notepad Automation Intent
            if any(k in command for k in ["open letter writer", "letter writer dialog", "show letter writer"]):
                return "LETTER_WRITER_OPEN"

            if is_letter_command(command) or self.context_state.get("pending_letter_writer"):
                res = process_letter_command(command, self.context_state, status_callback=self.ui_callback)
                if res:
                    return res

            
            # 0.0 Autonomous AI Agent Multi-Step Goal Execution
            if any(k in command for k in [
                "create presentation", "create ppt", "make ppt", "generate presentation",
                "organize downloads", "organize my downloads", "clean downloads",
                "create excel", "excel report", "make excel", "create word",
                "book hotel", "book flight", "book event", "book movie", "find flight", "find hotel",
                "autonomous task", "run agent", "agent goal", "prepare today's meeting notes"
            ]):
                try:
                    from ai_agent import run_agent_task
                    return run_agent_task(command, status_callback=self.ui_callback)
                except Exception as e:
                    print(f"[AGENT ROUTER ERROR] {e}")

            # 0.0 WhatsApp Desktop Full Voice Control Suite Intent
            if any(k in command for k in [
                "message to", "ko message", "ko msg", "open chat", "whatsapp chat", "bhej do",
                "voice call", "video call", "send photo", "send file", "next chat", "previous chat", "open group",
                "call karo", "call kar do", "ko call", "call on whatsapp", "whatsapp call", "whatsapp pe call", "call"
            ]):
                from whatsapp_automation import process_whatsapp_command
                res = process_whatsapp_command(command)
                if res:
                    speak(res)
                    return res

            # 0.0 Mobile Control Intents (PC-to-Mobile Execution)
            if any(k in command for k in ["ring phone", "phone ring", "phone bajao", "ring my phone", "phone dhundho"]):
                from android_bridge import android_bridge
                res = android_bridge.ring_phone()
                speak(res)
                return res

            if any(k in command for k in ["vibrate phone", "phone vibrate"]):
                from android_bridge import android_bridge
                res = android_bridge.vibrate_phone()
                speak(res)
                return res

            if "on phone" in command or "phone par" in command:
                from android_bridge import android_bridge
                app_target = command.replace("open", "").replace("kholo", "").replace("on phone", "").replace("phone par", "").strip()
                res = android_bridge.open_app_on_phone(app_target or "WhatsApp")
                speak(res)
                return res
            
            # 0.0 Proactive Action Confirmation Intent ("Haan kar do", "Kar do", "Do it")
            if any(k in command for k in ["haan kar do", "kar do", "haan kardo", "do it", "chala do", "khol do", "yes do it", "sure do it", "haan chala do", "khol de"]):
                from proactive_companion import get_and_clear_pending_action
                action = get_and_clear_pending_action()
                if action:
                    print(f"[PROACTIVE ACTION CONFIRMED] Executing pending action: {action}")
                    speak("Ji Shravani, performing action now!")
                    return action
                else:
                    return "Ji Shravani! Batayein kya perform karna hai?"

            # 0. Voice Security & Biometrics Routing
            if any(k in command for k in ["register voice", "voice registration", "add voice print"]):
                try:
                    from voice_auth import has_registered_voice_users, load_voice_encodings
                    users = list(load_voice_encodings().keys())
                    count = len(users)
                    return f"Voice Registration Module active. Currently registered users ({count}): {', '.join(users) if users else 'None'}. Use the UI dialog or Voice Security panel to record new biometrics."
                except Exception as e:
                    return f"Voice registration error: {e}"

            if any(k in command for k in ["voice auth status", "voice security", "check voice auth"]):
                try:
                    from voice_auth import has_registered_voice_users, load_voice_encodings
                    users = list(load_voice_encodings().keys())
                    if users:
                        return f"Voice Security System ONLINE. Registered profiles: {', '.join(users)}."
                    else:
                        return "Voice Security System ONLINE. No voice profiles registered yet. Speak 'register voice' to record your biometrics."
                except Exception as e:
                    return f"Voice security check error: {e}"

            # Intruder Detection System Intents
            if any(k in command for k in ["start intruder", "enable intruder", "intruder protection on", "enable security mode", "defence mode", "defence on", "defense chalu", "security on", "intruder on"]):
                return "INTRUDER_DETECT_START"

            if any(k in command for k in ["stop intruder", "disable intruder", "intruder protection off", "disable security mode", "defence off", "defense band", "security off"]):
                return "INTRUDER_DETECT_STOP"

            if any(k in command for k in ["check intruder log", "show intruder log", "intruder log", "show intruder evidence", "intruder photo"]):
                try:
                    from intruder_detector import get_intruder_logs
                    logs = get_intruder_logs()
                    if not logs:
                        return "Intruder Defense Log: Clean. No unauthorized intrusion incidents recorded."
                    count = len(logs)
                    last_time = logs[0].get("timestamp", "Unknown")
                    return f"Intruder Defense Log: {count} incident(s) recorded. Most recent intrusion detected at {last_time}. Evidence snapshots saved in jarvis_data/intruders/."
                except Exception as e:
                    return f"Intruder log check error: {e}"

            # ---------------- 4 NEXT-GEN SUPER FEATURES ----------------
            
            # 1. Anti-Spy Shoulder-Surfer Privacy Shield Intents
            if any(k in command for k in ["enable privacy shield", "privacy shield on", "start privacy shield", "anti spy on", "enable anti spy", "shoulder surfer protection", "anti spy protection", "privacy on", "privacy_shield_start"]):
                from shoulder_surfer_shield import shield_controller
                return shield_controller.start()

            if any(k in command for k in ["disable privacy shield", "privacy shield off", "stop privacy shield", "anti spy off", "disable anti spy", "privacy off"]):
                from shoulder_surfer_shield import shield_controller
                return shield_controller.stop()

            if any(k in command for k in ["test privacy shield", "demo privacy shield", "test anti spy"]):
                from shoulder_surfer_shield import shield_controller
                return shield_controller.test_shield()

            # 2. Touchless Air-Gesture Presentation Controller Intents
            if any(k in command for k in ["enable gesture control", "gesture control on", "start air gestures", "air gestures on", "touchless control on", "enable air gesture", "start gestures", "air gesture", "gesture_control_start"]):
                from air_gesture_controller import air_gesture_controller
                return air_gesture_controller.start()

            if any(k in command for k in ["disable gesture control", "gesture control off", "stop air gestures", "air gestures off", "touchless control off", "stop gestures"]):
                from air_gesture_controller import air_gesture_controller
                return air_gesture_controller.stop()

            # 3. Autonomous OS Doctor & Deep RAM Healing Intents
            if any(k in command for k in ["diagnose my system", "system diagnosis", "run system diagnosis", "diagnose system", "why is my pc slow", "fix slow pc", "boost my pc", "clean ram", "heal system", "os doctor", "ram boost", "optimize pc", "os_doctor_run"]):
                from os_doctor import run_system_diagnosis_and_healing
                return run_system_diagnosis_and_healing()

            # 4. Live Multimodal Screen Vision & Code Debugger Intent
            if any(k in command for k in [
                "what is on my screen", "what's on my screen", "explain my screen", "explain screen",
                "analyze my screen", "analyze screen", "see my screen", "debug this code",
                "debug this error", "find the bug on my screen", "what is this bug", "explain this diagram",
                "what is this architecture", "check my screen", "describe screen", "scan screen",
                "screen vision", "screen dekho", "screen explain karo", "screen dekh ke batao",
                "meri screen pe kya he", "screen pe kya hai", "kya chal rha he screen pe",
                "screen check karo", "check screen", "debug code", "debug error", "code error"
            ]):
                res = process_screenshot_command(command)
                if res:
                    return res

            # 5. Cyber Ocular Eye-Tracking Mouse & Double-Blink Clicker
            if any(k in command for k in [
                "disable eye mouse", "stop eye mouse", "eye mouse off", "stop eye tracking mouse",
                "eye tracking off", "turn off eye mouse", "aankhon se mouse band", "ankhon se mouse band",
                "eye_mouse_stop", "mouse off", "mouse band karo", "stop mouse", "disable mouse",
                "disable air mouse", "stop air mouse", "air mouse off"
            ]):
                from eye_mouse import eye_mouse_controller
                return eye_mouse_controller.stop()

            if any(k in command for k in [
                "enable eye mouse", "start eye mouse", "eye mouse on", "eye mouse",
                "eye tracking mouse", "turn on eye mouse", "ocular mouse", "eye cursor",
                "aankhon se mouse", "ankhon se mouse", "eye control", "double blink mouse",
                "eye_mouse_start", "mouse on", "mouse chalu karo", "start mouse", "mouse chalao", "enable mouse",
                "enable air mouse", "start air mouse", "air mouse on", "air mouse"
            ]):
                from eye_mouse import eye_mouse_controller
                return eye_mouse_controller.start()

            # 6. Air Canvas & Mid-Air Laser Writer Intents
            if any(k in command for k in ["close air canvas", "stop air writing", "air canvas off", "close canvas", "canvas band karo", "band karo canvas"]):
                return "AIR_CANVAS_CLOSE"

            if any(k in command for k in [
                "open air canvas", "enable air writing", "start air canvas", "air canvas on", "air canvas",
                "air canva", "canva writer", "air canva writer", "canvas writer", "air canvas writer",
                "air writing", "laser writer", "air sketcher", "drawing canvas", "open canvas",
                "canvas kholo", "air canvas kholo", "air_canvas_open"
            ]):
                return "AIR_CANVAS_OPEN"

            # 7. AI Posture & Ergonomics Sentinel Intents
            if any(k in command for k in ["disable posture sentinel", "posture guard off", "stop posture monitoring", "posture off"]):
                return "POSTURE_SENTINEL_STOP"

            if any(k in command for k in ["test posture sentinel", "demo posture sentinel", "test posture"]):
                return "POSTURE_SENTINEL_TEST"

            if any(k in command for k in ["enable posture sentinel", "posture guard on", "start posture monitoring", "posture sentinel on", "posture on", "monitor posture", "posture guard"]):
                return "POSTURE_SENTINEL_START"

            # 8. Iron Man Holographic Heads-Up Display (HUD) Intents
            if any(k in command for k in ["disengage hud", "close hud", "hud off", "disable hud", "hide hud"]):
                return "HOLOGRAPHIC_HUD_DISENGAGE"

            if any(k in command for k in ["engage holographic hud", "launch hud", "holographic hud on", "enable hud", "hud on", "iron man hud", "show hud", "open hud", "holographic_hud_engage"]):
                return "HOLOGRAPHIC_HUD_ENGAGE"
            
            # 9. AI Eye-Gaze & Attention Sentinel Intents
            if any(k in command for k in ["disable gaze", "gaze off", "stop gaze", "stop attention lock", "eye tracking off", "disable eye tracking"]):
                return "GAZE_TRACKER_STOP"

            if any(k in command for k in ["test gaze", "demo gaze", "test eye tracking", "demo attention lock"]):
                return "GAZE_TRACKER_TEST"

            if any(k in command for k in ["enable gaze", "gaze lock on", "start gaze", "start attention lock", "gaze tracking on", "eye tracking on", "enable eye tracking", "attention lock", "gaze lock", "eye gaze", "gaze_tracker_start"]):
                return "GAZE_TRACKER_START"

            # 10. Iron Man Floating Arc Reactor Desktop Orb Intents
            if any(k in command for k in ["hide arc reactor", "close arc reactor", "arc reactor off", "hide orb", "close orb"]):
                return "ARC_REACTOR_CLOSE"

            if any(k in command for k in ["launch arc reactor", "show arc reactor", "open arc reactor", "arc reactor on", "enable arc reactor", "desktop orb", "arc orb", "arc reactor"]):
                return "ARC_REACTOR_OPEN"

            # 11. Stark Protocol British Butler Voice Mode Intents
            if any(k in command for k in ["enable stark voice", "stark mode on", "british voice", "jarvis voice on", "stark protocol on", "stark mode"]):
                from voice_engine import set_stark_voice_mode
                set_stark_voice_mode(True)
                return "Stark Protocol voice online. British neural speech core initialized, Sir."

            if any(k in command for k in ["disable stark voice", "stark mode off", "indian voice", "standard voice", "default voice"]):
                from voice_engine import set_stark_voice_mode
                set_stark_voice_mode(False)
                return "Standard voice profile active."

            # 12. Touchless Air-Gesture Game: Stark Repulsor Strike Intents
            if any(k in command for k in [
                "play game", "launch game", "start game", "open game", "game chalu karo", "game khelo",
                "repulsor strike", "repulsor game", "stark game", "air gesture game", "gesture game",
                "play repulsor strike", "iron man game", "touchless game", "repulsor_game_open"
            ]):
                return "REPULSOR_GAME_OPEN"

            # Streamlit Analytics Dashboard Intent
            if any(k in command for k in ["open analytics", "show analytics", "analytics dashboard", "streamlit analytics", "open metrics", "analytics kholo"]):
                try:
                    import sys
                    import os
                    import subprocess
                    import webbrowser
                    from pathlib import Path
                    
                    project_root = Path(__file__).resolve().parent
                    venv_py = project_root / ".venv" / "Scripts" / "python.exe"
                    python_bin = str(venv_py) if venv_py.exists() else sys.executable
                    
                    cmd_launch = [python_bin, "-m", "streamlit", "run", "analytics_dashboard.py", "--server.port", "8501"]
                    subprocess.Popen(cmd_launch, cwd=str(project_root))
                    webbrowser.open("http://localhost:8501")
                    return "Launching Streamlit Analytics Dashboard at http://localhost:8501"
                except Exception as e:
                    return f"Failed to launch Analytics Dashboard: {e}"

            # Duplicate File Detector Intent
            if any(k in command for k in ["duplicate file", "scan duplicates", "find duplicates", "detect duplicates", "clean duplicates", "duplicate detector", "file detector", "open duplicate", "duplicate finder"]):
                return "DUPLICATE_FINDER_OPEN"

            # Meeting Notes Generator Intent
            if any(k in command for k in ["record meeting", "start meeting", "meeting notes", "meeting generator", "create meeting notes", "summarize meeting", "meeting note"]):
                return "MEETING_NOTES_OPEN"

            # AI Resume Analyzer Intent
            if any(k in command for k in ["analyze resume", "resume analyzer", "check my resume", "evaluate resume", "resume score", "fix resume", "check resume", "resume review"]):
                return "RESUME_ANALYZER_OPEN"

            # Real-Time News Intent (Direct Top 3 Speech/Text without opening window)
            if any(k in command for k in ["news btao", "news batao", "news sunao", "tell me news", "latest news", "today news", "today's news", "tech news", "sports news", "business news", "crypto news", "world news", "news"]):
                from news_researcher import get_quick_news_summary
                return get_quick_news_summary(command)

            if any(k in command for k in ["open news window", "news dialog", "research topic", "web research", "news research"]):
                return "NEWS_RESEARCHER_OPEN"

            # Encrypted Cyber Vault Intent
            if any(k in command for k in ["cyber vault", "password manager", "open vault", "vault kholo", "passwords", "api keys", "secret vault", "my passwords"]):
                return "CYBER_VAULT_OPEN"

            # AI Mock Interview Coach Intent
            if any(k in command for k in ["mock interview", "interview coach", "practice interview", "interview prep", "start interview", "mock test", "interview chalu"]):
                return "INTERVIEW_COACH_OPEN"

            # AI Face Dossier & Astro Profile Intent
            if any(k in command for k in ["face dossier", "scan face", "dossier", "dossier dikhao", "janam kundli", "kundli", "astro profile", "astro", "astrological profile", "face scanner", "face scan karo"]):
                return "FACE_DOSSIER_OPEN"

            # Ultron Dual AI Core Intents
            if any(k in command for k in ["ultron", "ultron mode", "activate ultron", "ultron ban jao", "ultron mode on", "no strings on me", "red alert"]):
                return "ULTRON_MODE_ACTIVATE"

            if any(k in command for k in ["jarvis mode", "activate jarvis", "jarvis ban jao", "jarvis mode on", "cyan mode", "stand down ultron"]):
                return "JARVIS_MODE_ACTIVATE"

            # 1. State Tracking (Memory Confirmation Prompt explicitly handles context)
            response = process_memory_command(command, self.context_state)
            
            # 2. General Tool Routing
            if not response: response = process_browser_command(command, self.context_state)
            if not response: response = process_system_command(command)
            if not response: response = process_conversation(command)
            if not response: response = process_notes_command(command)
            if not response: response = process_file_command(command)
            if not response: response = process_code_command(command)
            if not response: response = process_image_command(command)
            if not response: response = process_screenshot_command(command)
            if not response: response = process_ocr_command(command)
            if not response: response = process_excel_command(command)
            
            # 3. Utilities (Math, Time, Conversions, System Status)
            if not response:
                response = self.utilities.process_utility_command(command)

            # Return structure!
            if response:
                print(f"[ROUTER] Output generated: {response}")
                return response

            # Voice Typing Automation Intent
            if command.startswith("type ") or command.startswith("write ") or command.startswith("likho "):
                text_to_type = command.replace("type ", "").replace("write ", "").replace("likho ", "").strip()
                if text_to_type:
                    try:
                        import pyautogui
                        pyautogui.typewrite(text_to_type + " ", interval=0.02)
                        return f"Typed on screen: '{text_to_type}'"
                    except Exception:
                        return f"Voice typing requested: '{text_to_type}'."

            # Keep Close application Intent
            if command.startswith("close ") or command.startswith("band karo "):
                app_name = command.replace("close ", "").replace("band karo ", "").strip()
                if app_name:
                    success = close_app(app_name)
                    if success:
                        self.context_state['last_platform'] = None
                    return f"Terminating {app_name}." if success else f"I couldn't find {app_name} running."
                return "Which application should I close?"

            # Open application Intent (supports English + Hinglish "kholo")
            if command.startswith("open ") or command.startswith("kholo ") or command.startswith("launch ") or command.endswith(" kholo"):
                app_name = command.replace("open ", "").replace("kholo ", "").replace("launch ", "").replace(" kholo", "").strip()
                if "whatsapp web" in app_name:
                    return process_browser_command(command, self.context_state)
                
                if app_name not in ["google", "youtube", "instagram"]:
                    success = open_app(app_name)
                    if success: 
                        self.context_state['last_platform'] = None
                        return f"Opening {app_name} software."
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
