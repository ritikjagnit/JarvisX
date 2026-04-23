import sys
import ctypes

# 1. WINDOWS DPI AWARENESS FIX (Must be before any UI operations)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import threading
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication

from ui.dashboard import JarvisUI
from voice_engine import VOICE_INPUT_AVAILABLE, listen, speak
from command_engine import process_command
from command_router import CommandRouter
from voice_listener import VoiceListener
from voice_listener_vosk import VoiceListenerVosk
from command_worker import CommandWorker


# ---------------- BOOTSTRAP ----------------

def _bootstrap_local_site_packages():
    project_root = Path(__file__).resolve().parent

    candidate_paths = (
        project_root / ".venv" / "Lib" / "site-packages",
        project_root / ".venv-1" / "Lib" / "site-packages",
    )

    for site_packages in candidate_paths:
        if site_packages.exists():
            path_str = str(site_packages)
            if path_str not in sys.path:
                sys.path.insert(0, path_str)


_bootstrap_local_site_packages()


# ---------------- BRIDGE ----------------

class JarvisBridge(QObject):
    append_chat = pyqtSignal(str)
    set_voice_button_enabled = pyqtSignal(bool)
    set_voice_button_text = pyqtSignal(str)


# ---------------- MAIN APP ----------------

class JarvisApp:

    def __init__(self):

        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")

        # 2. START GLOBAL ANIMATIONS
        import ui.dashboard as dashboard
        dashboard.anim_controller = dashboard.AnimationController()
        dashboard.anim_controller.start()

        self.window = JarvisUI()
        self.bridge = JarvisBridge()
        self.voice_thread = None
        
        # Initialize continuous brain 
        self.command_router = CommandRouter(ui_callback=None) # Sub-callbacks stripped
        
        # 3. UPDATE WORKER / MAIN SYSTEM - Centralizes print/speak response
        def handle_response(response_text):
            self.bridge.append_chat.emit(f"Jarvis: {response_text}")
            
            # Avoid speaking fallback errors to prevent infinite loops and as per user request
            if response_text != "AI is not available right now":
                speak(response_text)
            else:
                print("[INFO] Speech suppressed for AI availability message.")
            
        # Initialize Central Queue worker
        self.worker = CommandWorker(
            command_router_callback=self.command_router.route,
            response_callback=handle_response
        )
        
        def voice_callback(cmd, source="voice"):
            self.bridge.append_chat.emit(f"You (Voice): {cmd}")
            # Insert into queue with high priority (1)
            self.worker.enqueue(cmd, source=source, priority=1)
            
        # Using standard listener (can swap to VoiceListenerVosk seamlessly here as needed)
        self.voice_listener = VoiceListener(command_callback=voice_callback, wake_word="")

        # UI connect (using custom wrapper for premium terminal styling)
        def add_to_chat(text):
            if text.startswith("Jarvis:"):
                msg = text.replace("Jarvis:", "").strip()
                self.window.terminal.append_message("JARVIS", msg)
            elif "Voice" in text:
                msg = text.replace("You (Voice):", "").strip()
                self.window.terminal.append_message("YOU", msg)
            else:
                msg = text.replace("You:", "").strip()
                self.window.terminal.append_message("YOU", msg)

        self.bridge.append_chat.connect(add_to_chat)
        self.bridge.set_voice_button_enabled.connect(self.window.voice_button.setEnabled)
        self.bridge.set_voice_button_text.connect(self.window.voice_button.setText)

        # buttons
        self.window.send_button.clicked.connect(self.handle_text_command)
        self.window.voice_button.clicked.connect(self.start_voice_thread)
        
        # New Button Connections (Dashboard Grid)
        self.window.scan_btn.clicked.connect(lambda: self.worker.enqueue("system scan", source="dashboard", priority=2))
        self.window.defense_btn.clicked.connect(lambda: self.worker.enqueue("security check", source="dashboard", priority=2))
        self.window.analytics_btn.clicked.connect(lambda: self.worker.enqueue("system metrics", source="dashboard", priority=2))
        self.window.settings_btn.clicked.connect(lambda: self.worker.enqueue("open settings", source="dashboard", priority=2))

        # voice status
        if not VOICE_INPUT_AVAILABLE:
            self.window.voice_button.setEnabled(False)
            self.window.voice_button.setText("Voice Unavailable")
            self.bridge.append_chat.emit("Jarvis: Voice not available. Checking local requirements...")
        else:
            self.bridge.append_chat.emit("Jarvis: Core systems online. Neural network ready.")
            self.bridge.append_chat.emit("Jarvis: [OFFLINE MODE] Ready for voice commands.")

    # ---------------- TEXT ----------------

    def handle_text_command(self):

        command = self.window.input_box.toPlainText().strip()

        if not command:
            return

        self.bridge.append_chat.emit(f"You: {command}")
        self.window.input_box.clear()

        # Push to multitasking queue system instead of executing directly!
        # Dashboard commands run at normal priority (2)
        self.worker.enqueue(command, source="dashboard", priority=2)

    # ---------------- VOICE ----------------

    def start_voice_thread(self):

        if not VOICE_INPUT_AVAILABLE:
            self.bridge.append_chat.emit("Jarvis: Voice not available.")
            return

        if getattr(self, 'voice_listener', None) and self.voice_listener.is_listening:
            # TOGGLE OFF: If it's already listening, turning it off
            self.voice_listener.stop_listening()
            self.bridge.set_voice_button_text.emit("Voice Command")
            self.bridge.append_chat.emit("Jarvis: Continuous Listening System Offline.")
        else:
            # TOGGLE ON: Start continuous listening in background
            self.bridge.set_voice_button_text.emit("Stop Listening")
            self.bridge.append_chat.emit("Jarvis: Continuous Listening Online. Minimizing to background...")
            self.voice_thread = threading.Thread(target=self.voice_listener.start_listening, daemon=True)
            self.voice_thread.start()

    # ---------------- RUN ----------------

    def run(self):

        self.window.show()

        # 🔥 STARTUP VOICE
        QTimer.singleShot(
            1000,
            lambda: speak("Systems online and fully initialized. Ready for commands, Boss.")
        )

        sys.exit(self.app.exec())


# ---------------- ENTRY ----------------

if __name__ == "__main__":
    jarvis = JarvisApp()
    jarvis.run()