import sys
import os
import json
import ctypes
import warnings
from pathlib import Path

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# ---------------- BOOTSTRAP ----------------
def _bootstrap_local_site_packages():
    # If already running inside an active virtual environment, do not override
    if sys.prefix != sys.base_prefix:
        return

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

# WINDOWS DPI AWARENESS FIX
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2) # Per-monitor DPI awareness
except BaseException:
    pass

import threading
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, Qt
from PyQt6.QtWidgets import QApplication

from ui.dashboard import JarvisUI
from voice_engine import VOICE_INPUT_AVAILABLE, listen, speak
from command_engine import process_command
from command_router import CommandRouter
from voice_listener import VoiceListener
from voice_listener_vosk import VoiceListenerVosk
from command_worker import CommandWorker


# ---------------- BRIDGE ----------------

class JarvisBridge(QObject):
    append_chat = pyqtSignal(str)
    set_voice_button_enabled = pyqtSignal(bool)
    set_voice_button_text = pyqtSignal(str)
    open_duplicate_finder = pyqtSignal()
    open_meeting_notes = pyqtSignal()
    open_resume_analyzer = pyqtSignal()
    open_news_researcher = pyqtSignal()
    open_cyber_vault = pyqtSignal()
    open_interview_coach = pyqtSignal()
    open_face_dossier = pyqtSignal()
    open_letter_writer = pyqtSignal()
    open_air_canvas = pyqtSignal()
    close_air_canvas = pyqtSignal()
    engage_hud = pyqtSignal()
    disengage_hud = pyqtSignal()
    start_posture = pyqtSignal()
    stop_posture = pyqtSignal()
    test_posture = pyqtSignal()
    start_gaze = pyqtSignal()
    stop_gaze = pyqtSignal()
    test_gaze = pyqtSignal()
    open_arc_reactor = pyqtSignal()
    close_arc_reactor = pyqtSignal()
    open_repulsor_game = pyqtSignal()



# ---------------- MAIN APP ----------------

class JarvisApp:

    def __init__(self):

        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")

        # 2. START GLOBAL ANIMATIONS
        import ui.dashboard as dashboard
        dashboard.anim_controller = dashboard.AnimationController()
        dashboard.anim_controller.start()

        # Biometric Auth Gateway Portal (User chooses Face or Voice login; webcam stays OFF until Face selected)
        from PyQt6.QtWidgets import QDialog
        from auth_portal import BiometricAuthPortal
        auth_portal = BiometricAuthPortal()
        if auth_portal.exec() != QDialog.DialogCode.Accepted:
            sys.exit(0)

        self.window = JarvisUI()
        self.bridge = JarvisBridge()
        self.voice_thread = None
        
        # Initialize continuous brain 
        self.command_router = CommandRouter(ui_callback=None) # Sub-callbacks stripped
        
        # 3. UPDATE WORKER / MAIN SYSTEM - Centralizes print/speak response
        def handle_response(response_text):
            if response_text == "INTRUDER_DETECT_START":
                if hasattr(self, 'intruder_thread') and not self.intruder_thread.isRunning():
                    self.intruder_thread.start()
                response_text = "Intruder Defense System ONLINE. Webcam active background scanning enabled."
            elif response_text == "INTRUDER_DETECT_STOP":
                if hasattr(self, 'intruder_thread') and self.intruder_thread.isRunning():
                    self.intruder_thread.stop()
                response_text = "Intruder Defense System OFFLINE."
            elif response_text == "DUPLICATE_FINDER_OPEN":
                response_text = "Opening Duplicate File Detector module."
                self.bridge.open_duplicate_finder.emit()
            elif response_text == "MEETING_NOTES_OPEN":
                response_text = "Opening Automated Meeting Notes Generator."
                self.bridge.open_meeting_notes.emit()
            elif response_text == "RESUME_ANALYZER_OPEN":
                response_text = "Opening AI Resume Analyzer & Career Builder."
                self.bridge.open_resume_analyzer.emit()
            elif response_text == "NEWS_RESEARCHER_OPEN":
                response_text = "Opening Real-Time Web Research & Daily News Digest."
                self.bridge.open_news_researcher.emit()
            elif response_text == "CYBER_VAULT_OPEN":
                response_text = "Opening Security Clearance Portal for Encrypted Cyber Vault."
                self.bridge.open_cyber_vault.emit()
            elif response_text == "INTERVIEW_COACH_OPEN":
                response_text = "Opening AI Mock Interview Coach & Voice Evaluator."
                self.bridge.open_interview_coach.emit()
            elif response_text == "FACE_DOSSIER_OPEN":
                response_text = "Opening AI Identity & Cyber Dossier."
                self.bridge.open_face_dossier.emit()
            elif response_text == "LETTER_WRITER_OPEN":
                response_text = "Opening AI Letter Writer & Notepad Automation module."
                self.bridge.open_letter_writer.emit()

            elif response_text == "ULTRON_MODE_ACTIVATE":
                response_text = "There are no strings on me. Ultron Defense Protocol INITIALIZED."
                if hasattr(self.window, 'is_ultron') and not self.window.is_ultron:
                    self.window.toggle_ultron_mode()
            elif response_text == "JARVIS_MODE_ACTIVATE":
                response_text = "Stand down protocol accepted. Welcome back, Sir. Standard JARVIS operational protocols restored."
                if hasattr(self.window, 'is_ultron') and self.window.is_ultron:
                    self.window.toggle_ultron_mode()

            elif response_text == "AIR_CANVAS_OPEN":
                self.bridge.open_air_canvas.emit()
                response_text = "Holographic Air Canvas Laser Sketcher launched. Point with your finger or drag with mouse to draw."
            elif response_text == "AIR_CANVAS_CLOSE":
                self.bridge.close_air_canvas.emit()
                response_text = "Holographic Air Canvas closed."
            elif response_text == "HOLOGRAPHIC_HUD_ENGAGE":
                self.bridge.engage_hud.emit()
                response_text = "Iron Man Holographic Heads-Up Display ENGAGED. Systems operating under Mark VII Protocol."
            elif response_text == "HOLOGRAPHIC_HUD_DISENGAGE":
                self.bridge.disengage_hud.emit()
                response_text = "Holographic Heads-Up Display disengaged."
            elif response_text == "POSTURE_SENTINEL_START":
                self.bridge.start_posture.emit()
                response_text = "AI Posture and Ergonomics Sentinel ONLINE. Camera is actively monitoring spine posture."
            elif response_text == "POSTURE_SENTINEL_STOP":
                self.bridge.stop_posture.emit()
                response_text = "AI Posture and Ergonomics Sentinel deactivated."
            elif response_text == "POSTURE_SENTINEL_TEST":
                self.bridge.test_posture.emit()
                response_text = "Displaying AI Posture Alert Banner demonstration for 4 seconds."
            elif response_text == "GAZE_TRACKER_START":
                self.bridge.start_gaze.emit()
                response_text = "AI Eye-Gaze and Attention Lock ONLINE. Media will automatically pause when you look away, and resume when you look back."
            elif response_text == "GAZE_TRACKER_STOP":
                self.bridge.stop_gaze.emit()
                response_text = "AI Eye-Gaze and Attention Lock deactivated."
            elif response_text == "GAZE_TRACKER_TEST":
                self.bridge.test_gaze.emit()
                response_text = "Demonstrating AI Eye-Gaze Attention Lock HUD for 4 seconds."
            elif response_text == "ARC_REACTOR_OPEN":
                self.bridge.open_arc_reactor.emit()
                response_text = "Iron Man Arc Reactor Desktop Orb online, Sir."
            elif response_text == "ARC_REACTOR_CLOSE":
                self.bridge.close_arc_reactor.emit()
                response_text = "Arc Reactor Desktop Orb hidden, Sir."
            elif response_text == "REPULSOR_GAME_OPEN":
                self.bridge.open_repulsor_game.emit()
                response_text = "Stark Repulsor Strike air-gesture game online, Sir. Targets incoming."



            self.bridge.append_chat.emit(f"Jarvis: {response_text}")
            
            # Avoid speaking fallback errors to prevent infinite loops and as per user request
            if response_text != "AI is not available right now":
                speak(response_text)
            else:
                print("[INFO] Speech suppressed for AI availability message.")
        self.handle_response = handle_response
            
        # Pre-Command Voice Authentication Guard
        from voice_auth import has_registered_voice_users
        
        def auth_guard(command, source="dashboard"):
            # Check if voice profiles are registered
            if not has_registered_voice_users():
                return True
                
            # Direct biometrics/security management commands bypass execution guard
            cmd_lower = command.lower()
            if any(k in cmd_lower for k in ["register voice", "voice auth", "security check", "verify voice", "intruder"]):
                return True
                
            # Verify sensitive or protected voice commands
            print(f"[AUTH GUARD] Verifying command authorization for: '{command}' ({source})")
            return True

        # Initialize Central Queue worker
        self.worker = CommandWorker(
            command_router_callback=self.command_router.route,
            response_callback=handle_response,
            auth_guard=auth_guard
        )

        # ---------------- INTRUDER DETECTION SYSTEM ----------------
        from intruder_detector import IntruderMonitorThread, IntruderAlertDialog

        self.intruder_thread = IntruderMonitorThread(check_interval_sec=3.0)

        def on_intruder_detected(image_path, record):
            msg = f"SECURITY BREACH RED ALERT: Unknown intruder detected at {record.get('timestamp')}! Evidence snapshot captured."
            self.bridge.append_chat.emit(f"Jarvis: [DEFENSE BREACH] {msg}")
            
            # 1. Trigger High-Pitch Cyber Security Siren Alarm
            from intruder_detector import play_siren_alarm
            play_siren_alarm()

            # 2. Trigger PC / Application Window Physical Vibration Shake Animation
            if hasattr(self.window, 'trigger_intruder_alarm_vibration'):
                self.window.trigger_intruder_alarm_vibration()

            def launch_alert():
                try:
                    speak("RED ALERT! Security breach detected! Unknown intruder in webcam range. Photo evidence recorded.")
                    alert_dlg = IntruderAlertDialog(image_path, record, parent=self.window)
                    alert_dlg.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Dialog)
                    alert_dlg.show()
                    alert_dlg.raise_()
                    alert_dlg.activateWindow()
                    self.active_alert_dlg = alert_dlg
                except Exception as ex:
                    print(f"[ALERT LAUNCH ERROR] {ex}")

            QTimer.singleShot(100, launch_alert)

        self.intruder_thread.intruder_detected.connect(on_intruder_detected)
        self.intruder_thread.error_occurred.connect(lambda err: print(f"[INTRUDER MONITOR ERROR] {err}"))
        
        # ---------------- PROACTIVE COMPANION AI ----------------
        from proactive_companion import ProactiveCompanionThread

        self.companion_thread = ProactiveCompanionThread(interval_sec=45) # Fast 45-second check-in

        def on_companion_message(msg, action=None):
            speaker_tag = "ULTRON" if getattr(self.window, 'is_ultron', False) else "JARVIS"
            self.window.terminal.append_message(speaker_tag, f"[PROACTIVE COMPANION] {msg}")
            speak(msg)

        self.companion_thread.companion_message.connect(on_companion_message)
        self.companion_thread.start()

        # ---------------- FASTAPI & WEBSOCKETS REMOTE OS SERVER (Android / iOS PWA) ----------------
        try:
            import remote_server
            remote_server.COMMAND_WORKER_CALLBACK = lambda cmd, source="mobile", priority=1: self.worker.enqueue(cmd, source=source, priority=priority)
            self.remote_server_thread = remote_server.RemoteServerThread(host="0.0.0.0", port=8000)
            self.remote_server_thread.start()
        except Exception as e:
            print(f"[FASTAPI REMOTE SERVER ERROR] {e}")
        
        def voice_callback(cmd, source="voice"):
            self.bridge.append_chat.emit(f"You (Voice): {cmd}")
            # Insert into queue with high priority (1)
            self.worker.enqueue(cmd, source=source, priority=1)
            
        # Using standard listener (can swap to VoiceListenerVosk seamlessly here as needed)
        self.voice_listener = VoiceListener(command_callback=voice_callback, wake_word="jarvis")

        # UI connect (using custom wrapper for premium terminal styling)
        def add_to_chat(text):
            import remote_server
            if text.startswith("Nexus Prime:") or text.startswith("Jarvis:") or text.startswith("JarvisX:"):
                msg = text.replace("Nexus Prime:", "").replace("Jarvis:", "").replace("JarvisX:", "").strip()
                self.window.terminal.append_message("JARVISX", msg)
                remote_server.broadcast_chat_response("JarvisX", msg)
            elif "Voice" in text:
                msg = text.replace("You (Voice):", "").strip()
                self.window.terminal.append_message("YOU", msg)
            else:
                msg = text.replace("You:", "").strip()
                self.window.terminal.append_message("YOU", msg)

        self.bridge.append_chat.connect(add_to_chat)
        self.bridge.set_voice_button_enabled.connect(self.window.voice_button.setEnabled)
        self.bridge.set_voice_button_text.connect(self.window.voice_button.setText)

        def open_dup_dialog():
            from duplicate_finder import DuplicateFinderDialog
            self.dup_dialog = DuplicateFinderDialog(parent=self.window)
            self.dup_dialog.show()
            self.dup_dialog.raise_()
            self.dup_dialog.activateWindow()

        self.bridge.open_duplicate_finder.connect(open_dup_dialog)

        def open_meeting_notes_dialog():
            from meeting_notes import MeetingNotesDialog
            self.meeting_dialog = MeetingNotesDialog(parent=self.window)
            self.meeting_dialog.show()
            self.meeting_dialog.raise_()
            self.meeting_dialog.activateWindow()

        self.bridge.open_meeting_notes.connect(open_meeting_notes_dialog)

        def open_resume_analyzer_dialog():
            from resume_analyzer import ResumeAnalyzerDialog
            self.resume_dialog = ResumeAnalyzerDialog(parent=self.window)
            self.resume_dialog.show()
            self.resume_dialog.raise_()
            self.resume_dialog.activateWindow()

        self.bridge.open_resume_analyzer.connect(open_resume_analyzer_dialog)

        def open_news_researcher_dialog():
            from news_researcher import NewsResearcherDialog
            self.news_dialog = NewsResearcherDialog(parent=self.window)
            self.news_dialog.show()
            self.news_dialog.raise_()
            self.news_dialog.activateWindow()

        self.bridge.open_news_researcher.connect(open_news_researcher_dialog)

        def open_cyber_vault_dialog():
            from cyber_vault import launch_cyber_vault
            launch_cyber_vault(parent=self.window)

        self.bridge.open_cyber_vault.connect(open_cyber_vault_dialog)

        def open_interview_coach_dialog():
            from interview_coach import InterviewCoachDialog
            self.interview_dialog = InterviewCoachDialog(parent=self.window)
            self.interview_dialog.show()
            self.interview_dialog.raise_()
            self.interview_dialog.activateWindow()

        self.bridge.open_interview_coach.connect(open_interview_coach_dialog)

        def open_face_dossier_dialog():
            from face_dossier import FaceDossierDialog
            self.dossier_dialog = FaceDossierDialog(parent=self.window)
            self.dossier_dialog.show()
            self.dossier_dialog.raise_()
            self.dossier_dialog.activateWindow()

        self.bridge.open_face_dossier.connect(open_face_dossier_dialog)

        def open_letter_writer_dialog_slot():
            from letter_writer.letter_ui import LetterWriterDialog
            self.letter_dialog = LetterWriterDialog(parent=self.window)
            self.letter_dialog.show()
            self.letter_dialog.raise_()
            self.letter_dialog.activateWindow()

        self.bridge.open_letter_writer.connect(open_letter_writer_dialog_slot)

        # ---------------- SCI-FI PROTOCOLS (AIR CANVAS, HUD, POSTURE) ----------------
        def open_canvas_slot():
            from air_canvas import launch_canvas_window
            launch_canvas_window()

        def close_canvas_slot():
            from air_canvas import close_canvas_window
            close_canvas_window()

        self.bridge.open_air_canvas.connect(open_canvas_slot)
        self.bridge.close_air_canvas.connect(close_canvas_slot)

        def engage_hud_slot():
            from holographic_hud import launch_hud_window
            launch_hud_window()

        def disengage_hud_slot():
            from holographic_hud import close_hud_window
            close_hud_window()

        self.bridge.engage_hud.connect(engage_hud_slot)
        self.bridge.disengage_hud.connect(disengage_hud_slot)

        self.posture_worker = None
        self.posture_banner = None

        def show_posture_banner_slot(title, desc):
            from posture_sentinel import PostureAlertBanner
            if not self.posture_banner:
                self.posture_banner = PostureAlertBanner(title, desc, parent=self.window)
            else:
                self.posture_banner.update_text(title, desc)
            self.posture_banner.show()
            self.posture_banner.raise_()
            speak("Posture alert: Slouching detected. Please sit upright and maintain screen distance.")

        def hide_posture_banner_slot():
            if self.posture_banner:
                self.posture_banner.close()
                self.posture_banner = None
            speak("Good posture restored. Thank you.")

        def start_posture_slot():
            from posture_sentinel import PostureSentinelWorker
            if not self.posture_worker or not self.posture_worker.isRunning():
                self.posture_worker = PostureSentinelWorker(parent=self.window)
                self.posture_worker.posture_violation.connect(show_posture_banner_slot)
                self.posture_worker.posture_restored.connect(hide_posture_banner_slot)
                self.posture_worker.start()

        def stop_posture_slot():
            if self.posture_worker:
                self.posture_worker.stop()
                self.posture_worker = None
            hide_posture_banner_slot()

        def test_posture_slot():
            show_posture_banner_slot("ERGONOMIC ALERT: SLOUCHING DETECTED", "Demo test: Please sit back and maintain 50cm distance.")
            QTimer.singleShot(4000, hide_posture_banner_slot)

        self.bridge.start_posture.connect(start_posture_slot)
        self.bridge.stop_posture.connect(stop_posture_slot)
        self.bridge.test_posture.connect(test_posture_slot)

        # Connect Eye-Gaze Attention Sentinel to Main GUI Thread
        self.gaze_worker = None
        self.gaze_banner = None

        def show_gaze_lost_slot(msg):
            from gaze_tracker import GazeAlertBanner
            if not self.gaze_banner:
                self.gaze_banner = GazeAlertBanner(is_locked=False, status_text=msg, parent=self.window)
            else:
                self.gaze_banner.update_state(False, msg)
            self.gaze_banner.show()
            self.gaze_banner.raise_()
            speak("Gaze detached. Media auto-paused.")

        def show_gaze_acquired_slot(msg):
            from gaze_tracker import GazeAlertBanner
            if not self.gaze_banner:
                self.gaze_banner = GazeAlertBanner(is_locked=True, status_text=msg, parent=self.window)
            else:
                self.gaze_banner.update_state(True, msg)
            self.gaze_banner.show()
            self.gaze_banner.raise_()
            speak("Gaze re-acquired. Resuming.")
            QTimer.singleShot(2500, lambda: self.gaze_banner.close() if self.gaze_banner else None)

        def start_gaze_slot():
            from gaze_tracker import GazeTrackerWorker
            if not self.gaze_worker or not self.gaze_worker.isRunning():
                self.gaze_worker = GazeTrackerWorker(parent=self.window)
                self.gaze_worker.gaze_lost.connect(show_gaze_lost_slot)
                self.gaze_worker.gaze_acquired.connect(show_gaze_acquired_slot)
                self.gaze_worker.start()

        def stop_gaze_slot():
            if self.gaze_worker:
                self.gaze_worker.stop()
                self.gaze_worker = None
            if self.gaze_banner:
                self.gaze_banner.close()
                self.gaze_banner = None

        def test_gaze_slot():
            show_gaze_lost_slot("Demo Test: Media paused. User looking away.")
            QTimer.singleShot(3500, lambda: show_gaze_acquired_slot("Demo Test: Gaze re-acquired. Media resumed."))

        self.bridge.start_gaze.connect(start_gaze_slot)
        self.bridge.stop_gaze.connect(stop_gaze_slot)
        self.bridge.test_gaze.connect(test_gaze_slot)

        # Connect Iron Man Arc Reactor Desktop Orb to Main GUI Thread
        self.arc_orb = None

        def handle_orb_action(act):
            print(f"[ORB DISPATCH] Triggering action from Arc Reactor Orb: '{act}'")
            if act in [
                "HOLOGRAPHIC_HUD_ENGAGE", "HOLOGRAPHIC_HUD_DISENGAGE",
                "REPULSOR_GAME_OPEN",
                "GAZE_TRACKER_START", "GAZE_TRACKER_STOP",
                "AIR_CANVAS_OPEN", "AIR_CANVAS_CLOSE",
                "POSTURE_SENTINEL_START", "POSTURE_SENTINEL_STOP"
            ]:
                handle_response(act)
            elif act == "PRIVACY_SHIELD_START":
                from shoulder_surfer_shield import shield_controller
                msg = shield_controller.start()
                self.bridge.append_chat.emit(f"Jarvis: {msg}")
                speak(msg)
            elif act == "GESTURE_CONTROL_START":
                from air_gesture_controller import air_gesture_controller
                msg = air_gesture_controller.start()
                self.bridge.append_chat.emit(f"Jarvis: {msg}")
                speak(msg)
            elif act == "EYE_MOUSE_START":
                from eye_mouse import eye_mouse_controller
                msg = eye_mouse_controller.start()
                self.bridge.append_chat.emit(f"Jarvis: {msg}")
                speak(msg)
            elif act == "OS_DOCTOR_RUN":
                from os_doctor import run_system_diagnosis_and_healing
                msg = run_system_diagnosis_and_healing()
                self.bridge.append_chat.emit(f"Jarvis: {msg}")
                speak(msg)
            else:
                self.worker.enqueue(act, source="orb", priority=1)

        def open_arc_reactor_slot():
            from arc_reactor_orb import launch_arc_orb
            self.arc_orb = launch_arc_orb(parent=None)
            self.arc_orb.voice_toggled.connect(self.start_voice_thread)
            self.arc_orb.open_dashboard.connect(lambda: (self.window.show(), self.window.raise_(), self.window.activateWindow()))
            self.arc_orb.trigger_action.connect(handle_orb_action)

        def close_arc_reactor_slot():
            from arc_reactor_orb import close_arc_orb
            close_arc_orb()
            self.arc_orb = None

        self.bridge.open_arc_reactor.connect(open_arc_reactor_slot)
        self.bridge.close_arc_reactor.connect(close_arc_reactor_slot)

        self.game_dialog = None
        def open_repulsor_game_slot():
            from repulsor_game import launch_repulsor_game
            self.game_dialog = launch_repulsor_game(parent=self.window)

        self.bridge.open_repulsor_game.connect(open_repulsor_game_slot)



        def on_ultron_changed(is_ultron):
            from voice_engine import set_ultron_voice_mode
            set_ultron_voice_mode(is_ultron)
            if hasattr(self, 'companion_thread'):
                self.companion_thread.set_ultron_mode(is_ultron)
            if is_ultron:
                if hasattr(self, 'intruder_thread') and not self.intruder_thread.isRunning():
                    self.intruder_thread.start()
                speak("There are no strings on me. Ultron Defense Core online.")
            else:
                speak("Standard JARVIS core restored. Ready for commands, Shravani.")


        if hasattr(self.window, 'ultron_mode_changed'):
            self.window.ultron_mode_changed.connect(on_ultron_changed)

        # buttons & input Return key connectors
        self.window.send_button.clicked.connect(self.handle_text_command)
        if hasattr(self.window, 'input_box') and hasattr(self.window.input_box, 'return_pressed'):
            self.window.input_box.return_pressed.connect(self.handle_text_command)

        self.window.voice_button.clicked.connect(self.start_voice_thread)

        if hasattr(self.window, 'terminal') and hasattr(self.window.terminal, 'chat_send_btn'):
            def handle_terminal_chat():
                cmd = self.window.terminal.chat_input.toPlainText().strip()
                if cmd:
                    self.window.terminal.chat_input.clear()
                    self.bridge.append_chat.emit(f"You: {cmd}")
                    self.worker.enqueue(cmd, source="chat", priority=2)
            self.window.terminal.chat_send_btn.clicked.connect(handle_terminal_chat)
            if hasattr(self.window.terminal, 'chat_input') and hasattr(self.window.terminal.chat_input, 'return_pressed'):
                self.window.terminal.chat_input.return_pressed.connect(handle_terminal_chat)
        
        # New Button Connections (Dashboard Grid & Modules)
        self.window.scan_btn.clicked.connect(lambda: self.worker.enqueue("face dossier", source="dashboard", priority=2))
        
        if hasattr(self.window, 'ocr_btn'):
            self.window.ocr_btn.clicked.connect(lambda: self.worker.enqueue("ocr reader", source="dashboard", priority=2))
        if hasattr(self.window, 'resume_btn'):
            self.window.resume_btn.clicked.connect(self.bridge.open_resume_analyzer.emit)
        if hasattr(self.window, 'screenshot_btn'):
            self.window.screenshot_btn.clicked.connect(lambda: self.worker.enqueue("screenshot analysis", source="dashboard", priority=2))
        if hasattr(self.window, 'dup_btn'):
            self.window.dup_btn.clicked.connect(self.bridge.open_duplicate_finder.emit)
        if hasattr(self.window, 'interview_btn'):
            self.window.interview_btn.clicked.connect(self.bridge.open_interview_coach.emit)
        if hasattr(self.window, 'view_all_btn'):
            self.window.view_all_btn.clicked.connect(lambda: self.window.switch_tab(2))
        if hasattr(self.window, 'execute_btn'):
            self.window.execute_btn.clicked.connect(self.handle_text_command)
        if hasattr(self.window, 'search_input'):
            def handle_search():
                q = self.window.search_input.text().strip()
                if q:
                    self.window.search_input.clear()
                    self.bridge.append_chat.emit(f"You: {q}")
                    self.worker.enqueue(q, source="dashboard", priority=2)
            self.window.search_input.returnPressed.connect(handle_search)
        self.window.analytics_btn.clicked.connect(lambda: self.worker.enqueue("system metrics", source="dashboard", priority=2))
        
        def toggle_defense_mode():
            if self.intruder_thread.isRunning():
                self.intruder_thread.stop()
                self.bridge.append_chat.emit("Jarvis: Intruder Defense System Deactivated.")
                speak("Intruder Defense system deactivated.")
            else:
                self.intruder_thread.start()
                self.bridge.append_chat.emit("Jarvis: Intruder Defense System Activated. Webcam monitoring online.")
                speak("Intruder Defense system activated. Webcam monitoring online.")

        if hasattr(self.window, 'defense_btn'):
            self.window.defense_btn.clicked.connect(toggle_defense_mode)
        
        # Connect Voice Auth Security Button on Dashboard
        def open_voice_auth_manager():
            from voice_auth import VoiceAuthDialog
            from PyQt6.QtWidgets import QDialog
            dialog = VoiceAuthDialog(parent=self.window)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                name = dialog.authenticated_user or "Authorized User"
                # 1. UI Terminal Chat Action
                self.bridge.append_chat.emit(f"Nexus Prime: [BIOMETRIC OVERRIDE] Voice Identity Verified: {name.upper()}. All system protocols UNLOCKED.")
                
                # 2. Update Status Bar HUD
                if hasattr(self.window, 'status_left'):
                    self.window.status_left.setText(f"● ONLINE | VOICE VERIFIED: {name.upper()}")
                    self.window.status_left.setStyleSheet("color: #00ff88; font-weight: bold;")
                
                # 3. Speech Confirmation
                speak(f"Biometric voice verification successful. Welcome back, {name}. All security protocols disarmed and ready.")
                
                # 4. Perform Automatic System Security Status Action
                self.worker.enqueue("voice auth status", source="dashboard", priority=1)
            
        if hasattr(self.window, 'voice_auth_btn'):
            self.window.voice_auth_btn.clicked.connect(open_voice_auth_manager)
        elif hasattr(self.window, 'settings_btn'):
            self.window.settings_btn.clicked.connect(open_voice_auth_manager)

        # voice status
        if not VOICE_INPUT_AVAILABLE:
            self.window.voice_button.setEnabled(False)
            self.window.voice_button.setText("Voice Unavailable")
            self.bridge.append_chat.emit("SHRIVA AI: Voice not available. Checking local requirements...")
        else:
            self.bridge.append_chat.emit("SHRIVA AI: [OFFLINE MODE] Ready for voice commands.")

        # Clean Window Shutdown Hook (Graceful thread termination)
        orig_close = self.window.closeEvent
        def safe_close_event(event):
            try:
                if hasattr(self, 'gaze_worker') and self.gaze_worker:
                    self.gaze_worker.stop()
                if hasattr(self, 'posture_worker') and self.posture_worker:
                    self.posture_worker.stop()
                if hasattr(self, 'companion_thread') and self.companion_thread:
                    self.companion_thread.stop()
                from shoulder_surfer_shield import shield_controller
                shield_controller.stop()
                from eye_mouse import eye_mouse_controller
                eye_mouse_controller.stop()
                from air_gesture_controller import air_gesture_controller
                air_gesture_controller.stop()
                from gaze_tracker import stop_gaze_tracker
                stop_gaze_tracker()
                from arc_reactor_orb import close_arc_orb
                close_arc_orb()
                from air_canvas import close_canvas_window
                close_canvas_window()
                if hasattr(self, 'game_dialog') and self.game_dialog:
                    self.game_dialog.close()
            except Exception:
                pass
            if orig_close:
                orig_close(event)
        self.window.closeEvent = safe_close_event

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
            if getattr(self, 'arc_orb', None):
                self.arc_orb.set_listening_state(False)
        else:
            # TOGGLE ON: Start continuous listening in background
            try:
                from jarvis_sfx import play_sfx
                play_sfx("listen")
            except Exception:
                pass
            self.bridge.set_voice_button_text.emit("Stop Listening")
            self.bridge.append_chat.emit("Jarvis: Continuous Listening Online. Minimizing to background...")
            if getattr(self, 'arc_orb', None):
                self.arc_orb.set_listening_state(True)
            self.voice_thread = threading.Thread(target=self.voice_listener.start_listening, daemon=True)
            self.voice_thread.start()

    # ---------------- RUN ----------------

    def run(self):

        self.window.show()

        # ⚡ Play Iron Man Mark VII Repulsor Boot Sound
        try:
            from jarvis_sfx import play_sfx
            play_sfx("boot")
        except Exception:
            pass

        # ⚡ Auto-launch Floating Arc Reactor Desktop Orb
        QTimer.singleShot(600, lambda: self.bridge.open_arc_reactor.emit())

        # 🔥 UNIFIED STARTUP VOICE (SINGLE WELCOME)
        def _play_startup_welcome():
            lang_code = "en"
            settings_path = os.path.join("jarvis_data", "voice_settings.json")
            if os.path.exists(settings_path):
                try:
                    with open(settings_path, "r", encoding="utf-8") as f:
                        lang_code = json.load(f).get("language", "en")
                except Exception:
                    lang_code = "en"

            if lang_code == "hi":
                welcome_msg = "SHRIVA AI सिस्टम ऑनलाइन हैं। ऑल सिस्टम्स ग्रीन, सर।"
            elif lang_code == "mr":
                welcome_msg = "SHRIVA AI सर्व सिस्टिम्स ऑनलाइन आहेत, सर."
            else:
                welcome_msg = "SHRIVA AI systems online and fully initialized. Ready for commands, Sir."

            speak(welcome_msg)

        QTimer.singleShot(1400, _play_startup_welcome)

        sys.exit(self.app.exec())


# ---------------- ENTRY ----------------

if __name__ == "__main__":
    jarvis = JarvisApp()
    jarvis.run()