import time
import cv2
import numpy as np
import pyautogui
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect, QApplication
)
from voice_engine import speak

class GazeAlertBanner(QDialog):
    """
    Futuristic floating cyber HUD badge displaying real-time
    eye-gaze attention lock and media auto-pause/resume status.
    """
    def __init__(self, is_locked=True, status_text="GAZE LOCKED: MEDIA ACTIVE", parent=None):
        super().__init__(parent)
        self.setWindowTitle("JARVIS GAZE SENTINEL")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(460, 95)

        # Position at top right
        screen = QApplication.primaryScreen()
        if screen:
            geom = screen.geometry()
            self.move(geom.width() - 480, 40)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setSpacing(4)

        # Glow shadow
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(28)
        self.card.setGraphicsEffect(self.shadow)

        self.title_label = QLabel("👁️ GAZE ATTENTION SENTINEL")
        self.title_label.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.card_layout.addWidget(self.title_label)

        self.status_label = QLabel(status_text)
        self.status_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.card_layout.addWidget(self.status_label)

        layout.addWidget(self.card)
        self.update_state(is_locked, status_text)

    def update_state(self, is_locked, text):
        if is_locked:
            border_col = "#00ffff"
            text_col = "#00ff88"
            glow_col = QColor(0, 255, 255, 160)
            self.title_label.setText("👁️ [ GAZE LOCKED | FOCUSED ]")
        else:
            border_col = "#f59e0b"
            text_col = "#f59e0b"
            glow_col = QColor(245, 158, 11, 180)
            self.title_label.setText("👁️ [ GAZE DETACHED | AUTO-PAUSED ]")

        self.card.setStyleSheet(f"""
            QFrame#card {{
                background: rgba(15, 23, 42, 0.95);
                border: 2px solid {border_col};
                border-radius: 14px;
                padding: 12px 18px;
            }}
            QLabel {{
                color: #ffffff;
                font-family: 'Segoe UI', Consolas;
            }}
        """)
        self.title_label.setStyleSheet(f"color: {border_col}; letter-spacing: 1px;")
        self.status_label.setStyleSheet(f"color: {text_col};")
        self.status_label.setText(text)
        self.shadow.setColor(glow_col)


class GazeTrackerWorker(QThread):
    """
    Computer Vision Eye-Gaze & Attention Sentinel.
    Uses 68 facial landmark topology to calculate Eye Aspect Ratio (EAR)
    and Head Pose Symmetry to detect if user is looking at the screen.
    Autonomously executes play/pause on visual attention state change.
    """
    gaze_lost = pyqtSignal(str)
    gaze_acquired = pyqtSignal(str)
    telemetry_updated = pyqtSignal(float, float, bool)

    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self.running = False

        # States
        self.is_focused = True
        self.lost_counter = 0
        self.acquired_counter = 0
        self.media_was_paused = False

    def _calc_ear(self, eye_pts):
        """Calculates Eye Aspect Ratio (EAR) for open eye detection."""
        p = np.array(eye_pts)
        A = np.linalg.norm(p[1] - p[5])
        B = np.linalg.norm(p[2] - p[4])
        C = np.linalg.norm(p[0] - p[3])
        return (A + B) / (2.0 * C + 1e-5)

    def run(self):
        self.running = True
        import face_recognition

        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(self.camera_index)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

        print("[GAZE-TRACKER] AI Eye-Gaze & Attention Sentinel ONLINE.")

        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.08)
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Downsample to 240x180 for lightning fast 15ms landmark inference
            small_rgb = cv2.resize(rgb, (0, 0), fx=0.5, fy=0.5)

            try:
                landmarks_list = face_recognition.face_landmarks(small_rgb)
            except Exception:
                landmarks_list = []

            currently_looking = False
            avg_ear = 0.0
            yaw_ratio = 1.0

            if landmarks_list and len(landmarks_list) > 0:
                lm = landmarks_list[0]
                left_eye = lm.get('left_eye', [])
                right_eye = lm.get('right_eye', [])
                nose_bridge = lm.get('nose_bridge', [])

                if left_eye and right_eye and nose_bridge:
                    # 1. Eye Aspect Ratio (Eyes Open Check)
                    ear_left = self._calc_ear(left_eye)
                    ear_right = self._calc_ear(right_eye)
                    avg_ear = (ear_left + ear_right) / 2.0

                    # 2. Horizontal Head Yaw Symmetry Check (Facing Screen Check)
                    left_center = np.mean(left_eye, axis=0)
                    right_center = np.mean(right_eye, axis=0)
                    nose_top = np.array(nose_bridge[0])

                    dist_l = np.linalg.norm(left_center - nose_top)
                    dist_r = np.linalg.norm(right_center - nose_top)
                    yaw_ratio = dist_l / (dist_r + 1e-5)

                    # Facing screen: Eyes open (EAR > 0.19) AND head facing forward (0.55 < yaw < 1.70)
                    if avg_ear > 0.19 and 0.52 < yaw_ratio < 1.75:
                        currently_looking = True

            self.telemetry_updated.emit(avg_ear, yaw_ratio, currently_looking)

            # State Machine with Debounce
            if currently_looking:
                self.lost_counter = 0
                self.acquired_counter += 1

                # If was looking away, restore focus after 3 consecutive frames (~300ms)
                if self.acquired_counter >= 3 and not self.is_focused:
                    self.is_focused = True
                    print("[GAZE-TRACKER] Gaze Re-Acquired -> RESUMING Media.")
                    if self.media_was_paused:
                        try:
                            pyautogui.press('space')
                            self.media_was_paused = False
                        except Exception:
                            pass
                    self.gaze_acquired.emit("Gaze Re-Acquired! Resuming active media.")
            else:
                self.acquired_counter = 0
                self.lost_counter += 1

                # If looked away for > 8 consecutive frames (~900ms)
                if self.lost_counter >= 8 and self.is_focused:
                    self.is_focused = False
                    print("[GAZE-TRACKER] Gaze Detached (User looking away) -> AUTO-PAUSING Media.")
                    try:
                        pyautogui.press('space')
                        self.media_was_paused = True
                    except Exception:
                        pass
                    self.gaze_lost.emit("Gaze Detached! Media auto-paused. Look back to resume.")

            time.sleep(0.09)  # ~11 FPS light inference

        cap.release()
        print("[GAZE-TRACKER] AI Eye-Gaze & Attention Sentinel OFFLINE.")

    def stop(self):
        self.running = False
        self.wait(1200)


# Global instances for standalone / bridge usage
active_gaze_worker = None
active_gaze_banner = None

def start_gaze_tracker(parent_window=None):
    global active_gaze_worker
    if active_gaze_worker and active_gaze_worker.isRunning():
        return active_gaze_worker

    worker = GazeTrackerWorker(parent=parent_window)
    active_gaze_worker = worker
    worker.start()
    return worker

def stop_gaze_tracker():
    global active_gaze_worker, active_gaze_banner
    if active_gaze_worker:
        active_gaze_worker.stop()
        active_gaze_worker = None
    if active_gaze_banner:
        active_gaze_banner.close()
        active_gaze_banner = None
