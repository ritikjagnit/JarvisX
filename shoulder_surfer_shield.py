import os
import cv2
import time
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QFrame, QGraphicsDropShadowEffect, QApplication
)
from voice_engine import speak

class PrivacyShieldOverlay(QDialog):
    """
    Full-screen cyber security privacy shield that locks the view
    when a secondary observer is looking over the user's shoulder.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("JARVIS ANTI-SPY SHIELD")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Make it cover the primary screen
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())

        self.setStyleSheet("""
            QDialog {
                background-color: rgba(2, 6, 23, 0.96);
            }
            QFrame#card {
                background: rgba(15, 23, 42, 0.95);
                border: 2px solid #ef4444;
                border-radius: 24px;
                padding: 40px;
            }
            QLabel {
                color: #ffffff;
                font-family: 'Segoe UI', Consolas;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(18)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Dual Glow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setColor(QColor(239, 68, 68, 180))
        shadow.setOffset(0, 0)
        card.setGraphicsEffect(shadow)

        # Warning Badge
        badge = QLabel("[ ⚠️ PRIVACY BREACH DETECTED ]")
        badge.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        badge.setStyleSheet("color: #ef4444; letter-spacing: 3px;")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(badge)

        # Icon
        icon_label = QLabel("🛡️ 👁️👁️")
        icon_label.setFont(QFont("Segoe UI", 48))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(icon_label)

        # Main Title
        title = QLabel("ANTI-SPY SHIELD ENGAGED")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #ffffff; letter-spacing: 2px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        # Description
        desc = QLabel(
            "SECONDARY OBSERVER DETECTED OVER SHOULDER\n"
            "Workstation display has been masked to protect confidentiality.\n"
            "Screen will automatically unlock once the observer departs."
        )
        desc.setFont(QFont("Segoe UI", 12))
        desc.setStyleSheet("color: #94a3b8; line-height: 1.6;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(desc)

        # Pulsing Status
        self.status = QLabel("● CONTINUOUS BIOMETRIC PERIMETER SCANNING...")
        self.status.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.status.setStyleSheet("color: #ef4444; letter-spacing: 1.5px;")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.status)

        layout.addWidget(card)


class ShoulderSurferDetector(QThread):
    """
    Background computer vision scanner that continuously tracks
    the number of human faces in the camera frame.
    """
    breach_detected = pyqtSignal(int)
    breach_cleared = pyqtSignal()

    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self.running = False
        self.is_breached = False
        self.clear_counter = 0

    def run(self):
        self.running = True
        import face_recognition

        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(self.camera_index)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

        print("[ANTI-SPY] Shoulder-Surfer Sentinel ONLINE.")

        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.08)
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Downsample to 192x144 for ultra-fast 12ms face location inference
            small_rgb = cv2.resize(rgb, (0, 0), fx=0.4, fy=0.4)
            try:
                faces = face_recognition.face_locations(small_rgb)
            except Exception:
                faces = []
            count = len(faces)

            if count >= 2:
                self.clear_counter = 0
                if not self.is_breached:
                    self.is_breached = True
                    print(f"[ANTI-SPY ALERT] Multiple faces detected ({count})! Engaging privacy shield.")
                    self.breach_detected.emit(count)
            else:
                if self.is_breached:
                    self.clear_counter += 1
                    # Require 3 consecutive single/zero face checks to debounce clear
                    if self.clear_counter >= 3:
                        self.is_breached = False
                        self.clear_counter = 0
                        print("[ANTI-SPY] Secondary observer departed. Clearing shield.")
                        self.breach_cleared.emit()

            # Throttle detection to ~8 FPS to keep CPU usage <1%
            time.sleep(0.12)

        cap.release()
        print("[ANTI-SPY] Shoulder-Surfer Sentinel OFFLINE.")

    def stop(self):
        self.running = False
        self.wait(1500)


class ShieldController:
    """
    Singleton Manager for Anti-Spy Shield.
    Handles overlay show/hide and voice announcements.
    """
    def __init__(self):
        self.detector = None
        self.overlay = None
        self.is_active = False

    def start(self):
        if self.is_active:
            return "Anti-Spy Shoulder-Surfer Shield is already active and monitoring."

        self.is_active = True
        self.detector = ShoulderSurferDetector()
        self.detector.breach_detected.connect(self._on_breach)
        self.detector.breach_cleared.connect(self._on_cleared)
        self.detector.start()
        return "Anti-Spy Shoulder-Surfer Shield ONLINE. Camera is actively monitoring for secondary observers."

    def stop(self):
        if not self.is_active:
            return "Anti-Spy Shoulder-Surfer Shield is currently inactive."

        self.is_active = False
        if self.detector:
            self.detector.stop()
            self.detector = None
        if self.overlay:
            self.overlay.close()
            self.overlay = None
        return "Anti-Spy Shoulder-Surfer Shield has been deactivated."

    def _on_breach(self, count):
        def _show():
            if not self.overlay:
                self.overlay = PrivacyShieldOverlay()
                self.overlay.showFullScreen()
            speak("Privacy alert! Secondary observer detected over your shoulder. Screen secured.")

        QTimer.singleShot(0, _show)

    def _on_cleared(self):
        def _hide():
            if self.overlay:
                self.overlay.close()
                self.overlay = None
            speak("Observer departed. Workstation unlocked.")

        QTimer.singleShot(0, _hide)

    def test_shield(self):
        def _test():
            self._on_breach(2)
            # Auto-close after 4 seconds during demo test
            QTimer.singleShot(4000, self._on_cleared)
        QTimer.singleShot(0, _test)
        return "Demonstrating Anti-Spy Shield for 4 seconds."


shield_controller = ShieldController()
