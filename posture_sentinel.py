import os
import time
import cv2
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect, QApplication
)
from voice_engine import speak

class PostureAlertBanner(QDialog):
    """
    Futuristic floating cyber banner that slides in at top-center
    when poor ergonomics, screen proximity, or slouching is detected.
    """
    def __init__(self, alert_title="ERGONOMIC ALERT: SLOUCHING DETECTED", alert_desc="Please sit upright and maintain at least 50cm screen distance.", parent=None):
        super().__init__(parent)
        self.setWindowTitle("JARVIS POSTURE SENTINEL")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(540, 120)

        screen = QApplication.primaryScreen()
        if screen:
            geom = screen.geometry()
            x = (geom.width() - 540) // 2
            self.move(x, 40)

        self.setStyleSheet("""
            QFrame#card {
                background: rgba(15, 23, 42, 0.96);
                border: 2px solid #f59e0b;
                border-radius: 16px;
                padding: 16px;
            }
            QLabel {
                color: #ffffff;
                font-family: 'Segoe UI', Consolas;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(6)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(245, 158, 11, 180))
        shadow.setOffset(0, 0)
        card.setGraphicsEffect(shadow)

        self.title_label = QLabel(f"🧘‍♂️ {alert_title}")
        self.title_label.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #f59e0b; letter-spacing: 1px;")
        card_layout.addWidget(self.title_label)

        self.desc_label = QLabel(alert_desc)
        self.desc_label.setFont(QFont("Segoe UI", 10))
        self.desc_label.setStyleSheet("color: #cbd5e1;")
        card_layout.addWidget(self.desc_label)

        layout.addWidget(card)

    def update_text(self, title, desc):
        self.title_label.setText(f"🧘‍♂️ {title}")
        self.desc_label.setText(desc)


class PostureSentinelWorker(QThread):
    """
    Background Computer Vision Ergonomics Sentinel.
    Uses DirectShow webcam feed with dynamic baseline calibration.
    """
    posture_violation = pyqtSignal(str, str)
    posture_restored = pyqtSignal()

    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self.running = False
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.is_slouching = False
        self.violation_counter = 0
        self.normal_counter = 0

    def run(self):
        self.running = True
        # Try DirectShow first on Windows for instantaneous hardware initialization
        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(self.camera_index)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

        print("[POSTURE-SENTINEL] Ergonomic Health AI Sentinel ONLINE.")

        # Baseline calibration (first 15 frames)
        calibrated = False
        calib_heights = []
        calib_y_centers = []
        base_h = 100
        base_y = 180

        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            h, w, _ = frame.shape
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=4, minSize=(50, 50))

            if len(faces) > 0:
                x, y, fw, fh = faces[0]
                fy = y + (fh / 2.0)

                if not calibrated:
                    calib_heights.append(fh)
                    calib_y_centers.append(fy)
                    if len(calib_heights) >= 12:
                        base_h = sum(calib_heights) / len(calib_heights)
                        base_y = sum(calib_y_centers) / len(calib_y_centers)
                        calibrated = True
                        print(f"[POSTURE-SENTINEL] Baseline Calibrated: base_h={base_h:.1f}, base_y={base_y:.1f}")
                else:
                    # Slouching / leaning too close: face size grew by >32%
                    too_close = fh > (base_h * 1.32)
                    # Slumping down in chair: head dropped down by >45 pixels
                    slumped = fy > (base_y + 45)

                    if too_close or slumped:
                        self.normal_counter = 0
                        self.violation_counter += 1
                        if self.violation_counter >= 4 and not self.is_slouching:
                            self.is_slouching = True
                            reason = "Too close to screen" if too_close else "Spine slouch detected"
                            desc = "You are leaning too close. Please sit back." if too_close else "Neck and spine are drooping. Please sit upright."
                            print(f"[POSTURE ALERT] {reason}")
                            self.posture_violation.emit(f"ERGONOMIC ALERT: {reason.upper()}", desc)
                    else:
                        self.violation_counter = 0
                        if self.is_slouching:
                            self.normal_counter += 1
                            if self.normal_counter >= 3:
                                self.is_slouching = False
                                self.normal_counter = 0
                                print("[POSTURE] Good posture restored.")
                                self.posture_restored.emit()

            time.sleep(0.12)  # ~8 FPS light background check

        cap.release()
        print("[POSTURE-SENTINEL] Ergonomic Health AI Sentinel OFFLINE.")

    def stop(self):
        self.running = False
        self.wait(1200)


# Global instances for main application
active_posture_worker = None
active_posture_banner = None

def start_posture_sentinel(parent_window=None):
    global active_posture_worker
    if active_posture_worker and active_posture_worker.isRunning():
        return active_posture_worker

    worker = PostureSentinelWorker(parent=parent_window)
    active_posture_worker = worker
    worker.start()
    return worker

def stop_posture_sentinel():
    global active_posture_worker, active_posture_banner
    if active_posture_worker:
        active_posture_worker.stop()
        active_posture_worker = None
    if active_posture_banner:
        active_posture_banner.close()
        active_posture_banner = None
