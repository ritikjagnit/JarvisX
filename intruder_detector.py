import os
import cv2
import json
import time
import numpy as np
from datetime import datetime

from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QFont, QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect
)
from voice_engine import speak
from face_auth import load_face_encodings

INTRUDERS_DIR = os.path.join("jarvis_data", "intruders")
INTRUDER_LOG_FILE = os.path.join("jarvis_data", "intruder_log.json")

def play_siren_alarm():
    """Plays a loud high-frequency cyber security siren alarm safely."""
    import threading
    def _siren_worker():
        try:
            from PyQt6.QtWidgets import QApplication
            for _ in range(6):
                QApplication.beep()
                time.sleep(0.12)
        except Exception:
            pass
    threading.Thread(target=_siren_worker, daemon=True).start()

# ----------------- EVIDENCE LOGGING & CAPTURE -----------------

def ensure_intruder_dirs():
    os.makedirs(INTRUDERS_DIR, exist_ok=True)

def save_intruder_evidence(frame, face_location=None, confidence=0):
    """
    Saves a timestamped snapshot of the intruder and updates the JSON log file.
    Returns (image_filepath, log_record).
    """
    ensure_intruder_dirs()
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    display_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"intruder_{timestamp_str}.jpg"
    filepath = os.path.join(INTRUDERS_DIR, filename)

    # Draw security HUD on snapshot image
    annotated_frame = frame.copy()
    h, w, ch = annotated_frame.shape

    # Red Border & Security Header
    cv2.rectangle(annotated_frame, (10, 10), (w - 10, h - 10), (0, 0, 255), 2)
    cv2.rectangle(annotated_frame, (10, 10), (w - 10, 45), (0, 0, 180), -1)
    cv2.putText(annotated_frame, f"SECURITY ALERT: UNKNOWN INTRUDER DETECTED [{display_time}]", 
                (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

    # Face Box if location available (top, right, bottom, left)
    if face_location:
        top, right, bottom, left = face_location
        cv2.rectangle(annotated_frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(annotated_frame, "UNAUTHORIZED SUBJECT", (left, max(top - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    # Save JPEG snapshot
    cv2.imwrite(filepath, annotated_frame)

    # Record Metadata in JSON Log
    record = {
        "id": timestamp_str,
        "timestamp": display_time,
        "image_path": filepath,
        "confidence": confidence,
        "status": "UNRESOLVED_INTRUDER"
    }

    logs = get_intruder_logs()
    logs.insert(0, record)
    
    with open(INTRUDER_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)

    return filepath, record

def get_intruder_logs():
    """Reads all past intruder incident logs."""
    if not os.path.exists(INTRUDER_LOG_FILE):
        return []
    try:
        with open(INTRUDER_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


# ----------------- BACKGROUND MONITOR THREAD -----------------

class IntruderMonitorThread(QThread):
    """
    Background thread that monitors the webcam for unknown faces.
    Runs non-intrusively after login without blocking UI.
    """
    intruder_detected = pyqtSignal(str, dict)  # Emits (image_path, log_record)
    status_message = pyqtSignal(str)           # Emits status message
    error_occurred = pyqtSignal(str)

    def __init__(self, check_interval_sec=1.0, camera_index=0):
        super().__init__()
        self.interval = check_interval_sec
        self.camera_index = camera_index
        self.running = False
        self.paused = False
        self.unknown_consecutive_count = 0
        self.required_consecutive = 2  # 2 consecutive checks (~2 sec) triggers alert fast
        self.last_alert_time = 0
        self.alert_cooldown = 10.0       # Cooldown between intruder alerts (seconds)

    def run(self):
        self.running = True
        self.status_message.emit("DEFENSE MONITOR ACTIVE: WEBCAM SCANNING ONLINE")
        
        # Lazy import face_recognition inside thread
        try:
            import face_recognition
        except ImportError:
            self.error_occurred.emit("face_recognition library not available for intruder detection.")
            return

        cap = cv2.VideoCapture(self.camera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not cap.isOpened():
            self.error_occurred.emit("Intruder monitor could not access system webcam.")
            return

        # Cache face encodings outside the loop
        known_faces = load_face_encodings()
        last_face_reload = time.time()

        while self.running:
            if self.paused:
                time.sleep(1.0)
                continue

            # Reload known encodings every 30s
            if time.time() - last_face_reload > 30:
                known_faces = load_face_encodings()
                last_face_reload = time.time()

            try:
                ret, frame = cap.read()
            except Exception as e:
                print(f"[INTRUDER MONITOR WARNING] Camera read error: {e}")
                time.sleep(0.5)
                continue

            if not ret or frame is None or frame.size == 0:
                time.sleep(0.5)
                continue

            # Downsample frame to 0.25x scale for 16x faster CPU face detection
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Detect faces in small frame
            face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")

            if face_locations:
                # If there are registered faces to check against
                if known_faces:
                    encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                    flat_known_encs = []
                    for val in known_faces.values():
                        if isinstance(val, list):
                            for item in val:
                                flat_known_encs.append(np.array(item))
                        else:
                            flat_known_encs.append(np.array(val))

                    is_intruder = False
                    intruder_loc = None

                    if flat_known_encs:
                        for idx, enc in enumerate(encodings):
                            distances = face_recognition.face_distance(flat_known_encs, enc)
                            min_dist = np.min(distances) if len(distances) > 0 else 1.0

                            # Match threshold: min_dist >= 0.60 means face does NOT match any registered user
                            if min_dist >= 0.60:
                                is_intruder = True
                                top, right, bottom, left = face_locations[idx]
                                intruder_loc = (top * 4, right * 4, bottom * 4, left * 4)
                                break

                    if is_intruder:
                        self.unknown_consecutive_count += 1
                        print(f"[DEFENSE ALERT] Unknown face detected! (Count {self.unknown_consecutive_count}/{self.required_consecutive})")

                        if self.unknown_consecutive_count >= self.required_consecutive:
                            now = time.time()
                            if now - self.last_alert_time >= self.alert_cooldown:
                                self.last_alert_time = now
                                self.unknown_consecutive_count = 0

                                # Capture evidence & trigger alert
                                img_path, record = save_intruder_evidence(frame, intruder_loc, confidence=int((1 - min_dist) * 100))
                                print(f"[DEFENSE] INTRUDER EVIDENCE SAVED: {img_path}")
                                self.intruder_detected.emit(img_path, record)
                    else:
                        # Recognized user face
                        self.unknown_consecutive_count = 0
                else:
                    # No authorized users registered -> treat any face as intruder
                    self.unknown_consecutive_count += 1
                    if self.unknown_consecutive_count >= self.required_consecutive:
                        now = time.time()
                        if now - self.last_alert_time >= self.alert_cooldown:
                            self.last_alert_time = now
                            self.unknown_consecutive_count = 0
                            top, right, bottom, left = face_locations[0]
                            intruder_loc = (top * 4, right * 4, bottom * 4, left * 4)
                            img_path, record = save_intruder_evidence(frame, intruder_loc, confidence=100)
                            self.intruder_detected.emit(img_path, record)
            else:
                self.unknown_consecutive_count = 0

            time.sleep(0.25) # Throttle loop to 4 FPS for 0% CPU overhead!

        cap.release()
        self.status_message.emit("DEFENSE MONITOR OFFLINE")

    def pause_monitor(self):
        self.paused = True

    def resume_monitor(self):
        self.paused = False

    def stop(self):
        self.running = False
        self.wait()


# ----------------- INTRUDER ALERT DIALOG UI -----------------

class IntruderAlertDialog(QDialog):
    """
    Red Holographic Cyberpunk Alert Window displaying intruder snapshot.
    """
    def __init__(self, image_path, record=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SHRIVA AI INTRUDER SECURITY ALERT")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.resize(620, 500)
        self.image_path = image_path
        self.record = record or {}

        self.setStyleSheet("""
            QDialog {
                background: #1a0307;
                border: 2px solid #ff0044;
                border-radius: 18px;
            }
            QLabel {
                color: #ffffff;
                border: none;
            }
            QPushButton {
                background: rgba(255, 0, 68, 0.2);
                color: #ff0044;
                border: 1.5px solid #ff0044;
                border-radius: 8px;
                padding: 10px 18px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(255, 0, 68, 0.45);
                color: #ffffff;
                border: 1.5px solid #ffffff;
            }
        """)

        # Red Glow Effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(255, 0, 68, 180))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header Title
        title_label = QLabel("⚠️ DEFENSE ALERT: UNKNOWN INTRUDER DETECTED")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ff0044; letter-spacing: 1px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Timestamp Info
        ts = self.record.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        info_label = QLabel(f"TIMESTAMP: {ts} | STATUS: EVIDENCE RECORDED")
        info_label.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        info_label.setStyleSheet("color: #ffaaaa;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        # Image Container
        self.image_container = QFrame()
        self.image_container.setMinimumHeight(300)
        self.image_container.setStyleSheet("border: 1px solid #ff0044; background: #000000; border-radius: 10px;")
        img_layout = QVBoxLayout(self.image_container)
        img_layout.setContentsMargins(5, 5, 5, 5)

        self.photo_label = QLabel()
        self.photo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img_layout.addWidget(self.photo_label)

        layout.addWidget(self.image_container)

        # Render Photo
        if os.path.exists(self.image_path):
            pixmap = QPixmap(self.image_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(580, 290, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.photo_label.setPixmap(scaled)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        dismiss_btn = QPushButton("🛡️ DISMISS ALERT")
        dismiss_btn.clicked.connect(self.accept)
        btn_layout.addWidget(dismiss_btn)

        layout.addLayout(btn_layout)
