import os
import cv2
import json
import time
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer, QPointF, QRectF
from PyQt6.QtGui import QImage, QPixmap, QFont, QPainter, QColor, QPen, QBrush, QLinearGradient, QRadialGradient
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, 
    QFrame, QGraphicsDropShadowEffect, QApplication
)
from voice_engine import speak
import threading

# File to store face encodings locally
ENCODINGS_FILE = os.path.join("jarvis_data", "face_auth.json")

def save_face_encoding(name, encoding):
    """Saves a face encoding list locally in a JSON file."""
    os.makedirs("jarvis_data", exist_ok=True)
    data = {}
    if os.path.exists(ENCODINGS_FILE):
        try:
            with open(ENCODINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass
    
    data[name.strip()] = encoding.tolist()
    with open(ENCODINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_face_encodings():
    """Loads face encodings from local JSON file."""
    if not os.path.exists(ENCODINGS_FILE):
        return {}
    try:
        with open(ENCODINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {name: np.array(enc) for name, enc in data.items()}
    except Exception:
        return {}

def has_registered_users():
    """Returns True if there is at least one registered face."""
    return len(load_face_encodings()) > 0


class FaceAuthWorker(QThread):
    """Thread worker responsible for processing camera frames and running face-recognition."""
    frame_ready = pyqtSignal(QImage, bool)  # Emits (processed_qimage, face_detected)
    authenticated = pyqtSignal(str)          # Emits the name of the authenticated user
    registration_done = pyqtSignal(str)      # Emits name when registration succeeds
    status_message = pyqtSignal(str, str)    # Emits (message, hex_color)
    error_occurred = pyqtSignal(str)

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.running = False
        self.mode = "auth"  # "auth" or "register"
        self.register_name = ""
        self.registered_faces = {}
        
        # Scan line variables
        self.scan_pos = 0.0
        self.scan_dir = 1
        
        # Authentication matching thresholds
        self.match_count = 0
        self.required_matches = 5  # Needs 5 consecutive matches to prevent false positives
        self.last_matched_name = None

        # Delay import of face_recognition to thread runtime
        self.face_recognition = None

    def run(self):
        self.running = True
        
        import sys
        import os
        import traceback
        from datetime import datetime

        log_path = "face_auth_debug.log"
        
        # Write section header to log file
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"\n--- DEBUG RUN: {datetime.now()} ---\n")
        except Exception:
            pass

        def log(msg):
            print(msg)
            try:
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(str(msg) + "\n")
            except Exception:
                pass

        log(f"sys.executable: {sys.executable}")
        log(f"sys.version: {sys.version}")
        log(f"Current Working Directory: {os.getcwd()}")

        try:
            import face_recognition
            self.face_recognition = face_recognition
            log(f"face_recognition.__file__: {face_recognition.__file__}")
        except Exception as e:
            tb_str = traceback.format_exc()
            log("--- IMPORT ERROR DETAILS ---")
            log(tb_str)
            log(f"Exception Type: {type(e).__name__}")
            log(f"Exception Message: {str(e)}")
            
            # Check if the face_recognition module itself is missing
            is_missing = False
            if isinstance(e, ModuleNotFoundError) and e.name == "face_recognition":
                is_missing = True
            elif isinstance(e, ImportError) and getattr(e, "name", None) == "face_recognition":
                is_missing = True
            elif "No module named 'face_recognition'" in str(e) and "face_recognition_models" not in str(e):
                is_missing = True

            if is_missing:
                error_msg = "face_recognition library is not installed."
            else:
                # Provide real exception details for sub-dependencies (dlib, DLLs, setuptools, etc.)
                error_msg = f"Dependency Failure: {type(e).__name__}: {str(e)}"

            log(f"Emitting error message to UI: {error_msg}")
            self.error_occurred.emit(error_msg)
            return

        self.registered_faces = load_face_encodings()
        cap = cv2.VideoCapture(self.camera_index)
        
        # Optimize camera resolution for processing speed
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        if not cap.isOpened():
            self.error_occurred.emit("Could not open system camera.")
            return

        self.status_message.emit("SYSTEM CAMERA ACTIVE - INITIALIZING SCANNER...", "#00ffff")

        while self.running:
            try:
                ret, frame = cap.read()
            except Exception as e:
                print(f"[FACE AUTH WARNING] Camera read error: {e}")
                time.sleep(0.05)
                continue

            if not ret or frame is None or frame.size == 0:
                time.sleep(0.03)
                continue

            # Mirror frame for intuitive UI display
            frame = cv2.flip(frame, 1)
            h, w, ch = frame.shape
            
            # Convert to RGB for face_recognition library
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect face locations
            face_locations = self.face_recognition.face_locations(rgb_frame, model="hog")
            face_detected = len(face_locations) > 0
            
            # Draw futuristic HUD elements onto frame
            self._draw_hud(frame, w, h)

            if face_detected:
                # We focus on the largest/first face detected
                face_loc = face_locations[0]
                top, right, bottom, left = face_loc
                
                # Draw high tech corner brackets
                self._draw_corner_brackets(frame, left, top, right, bottom, color=(255, 255, 0)) # BGR Cyan
                
                # Draw animated scan line inside the bounding box
                self._draw_scan_line(frame, left, top, right, bottom)
                
                if self.mode == "auth":
                    if self.registered_faces:
                        # Extract encoding
                        encodings = self.face_recognition.face_encodings(rgb_frame, [face_loc])
                        if encodings:
                            encoding = encodings[0]
                            # Compare face with all registered faces
                            known_encodings = list(self.registered_faces.values())
                            known_names = list(self.registered_faces.keys())
                            
                            # Calculate distance
                            distances = self.face_recognition.face_distance(known_encodings, encoding)
                            best_match_idx = np.argmin(distances) if len(distances) > 0 else -1
                            
                            # Match threshold (lower is stricter, 0.5 is safe and secure)
                            if best_match_idx != -1 and distances[best_match_idx] < 0.5:
                                name = known_names[best_match_idx]
                                confidence = int((1 - distances[best_match_idx]) * 100)
                                self.status_message.emit(f"MATCH IDENTIFIED: {name.upper()} ({confidence}%)", "#00ff88")
                                
                                # Corner brackets turn green
                                self._draw_corner_brackets(frame, left, top, right, bottom, color=(0, 255, 136)) # BGR Neon Green
                                cv2.putText(frame, f"{name.upper()} ({confidence}%)", (left, top - 10), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 136), 2)
                                
                                if name == self.last_matched_name:
                                    self.match_count += 1
                                else:
                                    self.match_count = 1
                                    self.last_matched_name = name
                                    
                                if self.match_count >= self.required_matches:
                                    self.status_message.emit("AUTHENTICATION PASSED - UNLOCKING SYSTEM...", "#00ff88")
                                    self.authenticated.emit(name)
                                    self.running = False
                                    break
                            else:
                                self.status_message.emit("BIOMETRIC ALERT: UNKNOWN FACE DETECTED", "#ff0066")
                                # Corner brackets turn red
                                self._draw_corner_brackets(frame, left, top, right, bottom, color=(102, 0, 255)) # BGR Neon Red
                                cv2.putText(frame, "UNKNOWN SUBJECT", (left, top - 10), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (102, 0, 255), 2)
                                self.match_count = 0
                                self.last_matched_name = None
                    else:
                        self.status_message.emit("NO REGISTERED FACES FOUND. REGISTER NOW.", "#ffaa00")
                        
                elif self.mode == "register":
                    self.status_message.emit("FACE TARGETED - PRESS 'CAPTURE FACE' TO CONFIRM", "#00ffff")
                    
                    # Capture request trigger
                    if self.register_name:
                        self.status_message.emit(f"EXTRACTING BIOMETRICS FOR {self.register_name.upper()}...", "#00ffff")
                        encodings = self.face_recognition.face_encodings(rgb_frame, [face_loc])
                        if encodings:
                            save_face_encoding(self.register_name, encodings[0])
                            self.registration_done.emit(self.register_name)
                            self.mode = "auth"
                            self.register_name = ""
                            self.registered_faces = load_face_encodings()  # Reload cache
                            self.match_count = 0
                        else:
                            self.status_message.emit("ERROR: Extraction failed. Try again.", "#ff0066")
                            self.register_name = ""
            else:
                self.status_message.emit("BIOMETRIC SCANNER: STANDBY - NO FACE IN RANGE", "#00ffff")
                self.match_count = 0
                self.last_matched_name = None

            # Convert frame to QImage for PyQt widget
            rgb_f = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            bytes_per_line = ch * w
            qimg = QImage(rgb_f.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.frame_ready.emit(qimg, face_detected)
            
            time.sleep(1/30) # Maintain ~30 FPS
            
        cap.release()

    def set_register_mode(self, name):
        """Switches the worker to registration mode to record a new face encoding."""
        self.register_name = name
        self.mode = "register"

    def stop(self):
        self.running = False
        self.wait()

    # OpenCV HUD Helper Methods
    def _draw_hud(self, frame, w, h):
        """Draws high tech cyberpunk holographic grid overlays onto the camera frame."""
        color = (255, 255, 0) # Cyan
        
        # Grid lines (faint)
        cv2.line(frame, (int(w/2), 0), (int(w/2), h), (255, 255, 0, 50), 1)
        cv2.line(frame, (0, int(h/2)), (w, int(h/2)), (255, 255, 0, 50), 1)
        
        # Crosshair center circle
        cv2.circle(frame, (int(w/2), int(h/2)), 40, color, 1)
        cv2.circle(frame, (int(w/2), int(h/2)), 5, color, -1)
        
        # HUD Border elements
        cv2.rectangle(frame, (10, 10), (w - 10, h - 10), color, 1)
        
        # Text Overlay
        cv2.putText(frame, "SYS.SECURITY.AUTH_V2", (20, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        cv2.putText(frame, f"FPS: 30 | LOCK: SECURE", (w - 180, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    def _draw_corner_brackets(self, img, left, top, right, bottom, color=(255, 255, 0), thickness=2, length=20):
        """Draws futuristic corners instead of a generic box."""
        # Top-Left corner
        cv2.line(img, (left, top), (left + length, top), color, thickness)
        cv2.line(img, (left, top), (left, top + length), color, thickness)
        
        # Top-Right corner
        cv2.line(img, (right, top), (right - length, top), color, thickness)
        cv2.line(img, (right, top), (right, top + length), color, thickness)
        
        # Bottom-Left corner
        cv2.line(img, (left, bottom), (left + length, bottom), color, thickness)
        cv2.line(img, (left, bottom), (left, bottom - length), color, thickness)
        
        # Bottom-Right corner
        cv2.line(img, (right, bottom), (right - length, bottom), color, thickness)
        cv2.line(img, (right, bottom), (right, bottom - length), color, thickness)

    def _draw_scan_line(self, frame, left, top, right, bottom):
        """Animates a cyan scanning bar moving vertically inside the face bounding box."""
        self.scan_pos += 0.05 * self.scan_dir
        if self.scan_pos > 1.0:
            self.scan_pos = 1.0
            self.scan_dir = -1
        elif self.scan_pos < 0.0:
            self.scan_pos = 0.0
            self.scan_dir = 1
            
        line_y = int(top + (bottom - top) * self.scan_pos)
        
        # Scanning line
        cv2.line(frame, (left, line_y), (right, line_y), (255, 255, 0), 2)
        
        # Sub-glow scanning bar
        overlay = frame.copy()
        cv2.rectangle(overlay, (left, top), (right, line_y), (255, 255, 0), -1)
        cv2.addWeighted(overlay, 0.1, frame, 0.9, 0, frame)


class FaceAuthDialog(QDialog):
    """Futuristic holographic dialog for face registration and authentication."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SHRIVA AI SECURITY ACCESS")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.resize(700, 600)
        self.authenticated_user = None
        self.is_authenticated = False
        
        # Setup modern dark glassmorphism theme
        self.setStyleSheet("""
            QDialog {
                background: #020617;
                border: 2px solid #00ffff;
                border-radius: 20px;
            }
            QLabel {
                color: #ffffff;
                border: none;
            }
            QPushButton {
                background: rgba(0, 255, 255, 0.1);
                color: #00ffff;
                border: 1.5px solid #00ffff;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                font-family: Arial;
                font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(0, 255, 255, 0.3);
                border: 1.5px solid #ffffff;
                color: #ffffff;
            }
            QLineEdit {
                background: rgba(15, 23, 42, 0.8);
                color: #00ffff;
                border: 1px solid #0066ff;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
        """)

        # Glow effect
        glow = QGraphicsDropShadowEffect()
        glow.setBlurRadius(20)
        glow.setColor(QColor(0, 255, 255, 150))
        glow.setOffset(0, 0)
        self.setGraphicsEffect(glow)

        self._init_ui()

        # Initialize thread
        self.worker = FaceAuthWorker()
        self.worker.frame_ready.connect(self.update_frame)
        self.worker.status_message.connect(self.update_status)
        self.worker.authenticated.connect(self.on_authenticated)
        self.worker.registration_done.connect(self.on_registration_done)
        self.worker.error_occurred.connect(self.on_error)
        
        # Auto-start authentication if faces already exist
        if has_registered_users():
            self.show_auth_mode()
            self.worker.start()
        else:
            self.show_register_mode()
            self.worker.start()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header Title
        self.title_label = QLabel("SYSTEM SECURITY GATE: BIOMETRIC LOGIN")
        self.title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #00ffff; letter-spacing: 2px;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Video Panel Container
        self.video_container = QFrame()
        self.video_container.setMinimumSize(600, 400)
        self.video_container.setStyleSheet("border: 1px solid #0066ff; background: #000; border-radius: 10px;")
        
        video_layout = QVBoxLayout(self.video_container)
        video_layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setText("BIOMETRIC CAMERA INITIALIZING...")
        self.video_label.setFont(QFont("Consolas", 14))
        self.video_label.setStyleSheet("color: #00ffff; border: none;")
        video_layout.addWidget(self.video_label)
        
        layout.addWidget(self.video_container)

        # Status HUD label
        self.status_label = QLabel("BIOMETRIC SCANNER: STANDBY")
        self.status_label.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #00ffff;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Inputs and Controls
        self.controls_layout = QHBoxLayout()
        self.controls_layout.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Authorized Username...")
        self.name_input.setVisible(False)
        self.controls_layout.addWidget(self.name_input)

        self.action_btn = QPushButton("REGISTER NEW FACE")
        self.action_btn.clicked.connect(self.handle_action_btn)
        self.controls_layout.addWidget(self.action_btn)

        self.voice_auth_btn = QPushButton("🎤 VOICE LOGIN / REGISTER")
        self.voice_auth_btn.clicked.connect(self.open_voice_auth)
        self.controls_layout.addWidget(self.voice_auth_btn)

        self.exit_btn = QPushButton("✕ TERMINATE SESSION")
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 0, 102, 0.1);
                color: #ff0066;
                border: 1.5px solid #ff0066;
            }
            QPushButton:hover {
                background: rgba(255, 0, 102, 0.3);
                border: 1.5px solid #ffffff;
                color: #ffffff;
            }
        """)
        self.exit_btn.clicked.connect(self.reject_session)
        self.controls_layout.addWidget(self.exit_btn)

        layout.addLayout(self.controls_layout)

    def open_voice_auth(self):
        """Opens Voice Authentication and Registration Dialog."""
        try:
            from voice_auth import VoiceAuthDialog as VDialog
            v_dialog = VDialog(parent=self)
            if v_dialog.exec() == QDialog.DialogCode.Accepted:
                self.authenticated_user = v_dialog.authenticated_user
                self.is_authenticated = True
                self.accept()
        except Exception as e:
            self.update_status(f"VOICE AUTH ERROR: {str(e).upper()}", "#ff0066")

    def show_auth_mode(self):
        """Configures the dialog widgets for authentication mode."""
        self.name_input.setVisible(False)
        self.action_btn.setText("REGISTER NEW FACE")
        self.title_label.setText("SYSTEM SECURITY GATE: BIOMETRIC LOGIN")
        self.status_label.setText("BIOMETRIC SCANNER: SCANNING...")
        self.status_label.setStyleSheet("color: #00ffff;")

    def show_register_mode(self):
        """Configures the dialog widgets for registration mode."""
        self.name_input.setVisible(True)
        self.name_input.clear()
        self.action_btn.setText("CAPTURE FACE")
        self.title_label.setText("NEW USER ENROLLMENT")
        self.status_label.setText("INPUT NAME AND LOOK DIRECTLY AT THE CAMERA")
        self.status_label.setStyleSheet("color: #ffaa00;")

    def handle_action_btn(self):
        """Routes action clicks between toggling registration and capturing face."""
        if self.action_btn.text() == "REGISTER NEW FACE":
            self.show_register_mode()
        elif self.action_btn.text() == "CAPTURE FACE":
            name = self.name_input.text().strip()
            if not name:
                self.update_status("ERROR: PLEASE ENTER A VALID USERNAME", "#ff0066")
                return
            self.worker.set_register_mode(name)

    def update_frame(self, qimg, face_detected):
        """Scale and render camera QImage to label."""
        pixmap = QPixmap.fromImage(qimg)
        scaled = pixmap.scaled(
            self.video_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        self.video_label.setPixmap(scaled)

    def update_status(self, message, hex_color):
        """Update system status label with color code."""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {hex_color}; font-weight: bold;")

    def on_authenticated(self, name):
        """Runs when user matches encodings."""
        self.authenticated_user = name
        self.is_authenticated = True
        
        # Run speech prompt on a detached background thread to prevent UI freezing
        def speak_success():
            speak(f"Access granted. Welcome back, {name}.")
            
        threading.Thread(target=speak_success, daemon=True).start()
        
        # Small delay to let user view ACCESS GRANTED HUD screen before main window pops up
        QTimer.singleShot(1500, self.accept)

    def on_registration_done(self, name):
        """Runs when face is captured and saved."""
        self.update_status(f"PROFILE RECORDED FOR {name.upper()}", "#00ff88")
        speak(f"Biometrics recorded for {name}. System initialized.")
        QTimer.singleShot(2000, self.show_auth_mode)

    def on_error(self, message):
        """Camera or package error handler."""
        self.update_status(f"SYSTEM FAILURE: {message.upper()}", "#ff0066")
        QTimer.singleShot(4000, self.reject_session)

    def reject_session(self):
        """Deny login access and terminate app."""
        self.is_authenticated = False
        self.worker.stop()
        self.reject()

    def closeEvent(self, event):
        self.worker.stop()
        super().closeEvent(event)
