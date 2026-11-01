import sys
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QMessageBox, QApplication, QGraphicsDropShadowEffect
)

from face_auth import FaceAuthDialog, load_face_encodings
from voice_auth import VoiceAuthDialog, load_voice_encodings


class BiometricAuthPortal(QDialog):
    """
    Holographic Cyberpunk Biometric Security Gateway Portal.
    Allows user to select between Face Recognition Login and Voice Biometric Login on startup
    WITHOUT turning on webcam hardware until selected.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SHRIVA AI BIOMETRIC SECURITY GATEWAY")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.resize(760, 520)
        self.authenticated_user = None

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #020617, stop:0.5 #090d16, stop:1 #020617);
                border: 2px solid #00ffff;
                border-radius: 24px;
            }
            QLabel {
                color: #ffffff;
                border: none;
            }
            QFrame#card_face {
                background: rgba(15, 23, 42, 0.85);
                border: 1.5px solid #00ffff;
                border-radius: 16px;
                padding: 18px;
            }
            QFrame#card_face:hover {
                border: 2px solid #00ffff;
                background: rgba(0, 255, 255, 0.12);
            }
            QFrame#card_voice {
                background: rgba(15, 23, 42, 0.85);
                border: 1.5px solid #00ff88;
                border-radius: 16px;
                padding: 18px;
            }
            QFrame#card_voice:hover {
                border: 2px solid #00ff88;
                background: rgba(0, 255, 136, 0.12);
            }
            QPushButton {
                background: rgba(0, 255, 255, 0.15);
                color: #00ffff;
                border: 1.5px solid #00ffff;
                border-radius: 10px;
                padding: 14px 22px;
                font-weight: bold;
                font-size: 14px;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: rgba(0, 255, 255, 0.45);
                color: #ffffff;
                border: 1.5px solid #ffffff;
            }
            QPushButton#primary_face {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 255, 255, 0.25), stop:1 rgba(0, 150, 255, 0.25));
                color: #00ffff;
                border: 1.5px solid #00ffff;
            }
            QPushButton#primary_face:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 255, 255, 0.6), stop:1 rgba(0, 150, 255, 0.6));
                color: #ffffff;
                border-color: #ffffff;
            }
            QPushButton#primary_voice {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 255, 136, 0.25), stop:1 rgba(0, 200, 100, 0.25));
                color: #00ff88;
                border: 1.5px solid #00ff88;
            }
            QPushButton#primary_voice:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 255, 136, 0.6), stop:1 rgba(0, 200, 100, 0.6));
                color: #ffffff;
                border-color: #ffffff;
            }
            QPushButton#reg_btn {
                background: rgba(168, 85, 247, 0.15);
                color: #a855f7;
                border: 1.5px solid #a855f7;
                border-radius: 10px;
                padding: 10px 18px;
                font-size: 13px;
            }
            QPushButton#reg_btn:hover {
                background: rgba(168, 85, 247, 0.4);
                color: #ffffff;
                border-color: #ffffff;
            }
            QPushButton#exit_btn {
                background: rgba(255, 0, 68, 0.15);
                color: #ff0044;
                border: 1.5px solid #ff0044;
                border-radius: 10px;
                padding: 10px 18px;
                font-size: 13px;
            }
            QPushButton#exit_btn:hover {
                background: rgba(255, 0, 68, 0.45);
                color: #ffffff;
                border-color: #ffffff;
            }
        """)

        # Dual Glow Effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 255, 255, 160))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(18)

        # Top Badge
        badge = QLabel("[ SECURITY OVERRIDE PROTOCOL 704 ]")
        badge.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        badge.setStyleSheet("color: #00ffff; letter-spacing: 2px;")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(badge)

        # Header Title
        title_label = QLabel("⚡ SHRIVA AI BIOMETRIC SECURITY GATEWAY")
        title_label.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #ffffff; letter-spacing: 1.5px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        sub_label = QLabel("SELECT YOUR BIOMETRIC ACCESS MODE TO UNLOCK SYSTEM PROTOCOLS")
        sub_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        sub_label.setStyleSheet("color: #64748b; letter-spacing: 0.5px;")
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub_label)

        # Status Banner
        faces_count = len(load_face_encodings())
        voices_count = len(load_voice_encodings())

        status_text = f"● PROFILES ENROLLED:   👤 {faces_count} Face Print(s)   |   🎤 {voices_count} Voice Print(s)"
        status_banner = QLabel(status_text)
        status_banner.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        status_banner.setStyleSheet("color: #00ff88; background: rgba(0, 255, 136, 0.08); border: 1px solid rgba(0, 255, 136, 0.3); border-radius: 10px; padding: 10px;")
        status_banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(status_banner)

        # Options Container Cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(22)

        # CARD 1: FACE LOGIN
        face_card = QFrame()
        face_card.setObjectName("card_face")
        fc_layout = QVBoxLayout(face_card)
        fc_layout.setSpacing(12)

        fc_badge = QLabel("[ WEBCAM SCANNER ]")
        fc_badge.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        fc_badge.setStyleSheet("color: #00ffff;")
        fc_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fc_layout.addWidget(fc_badge)

        fc_icon = QLabel("👤")
        fc_icon.setFont(QFont("Segoe UI", 38))
        fc_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fc_layout.addWidget(fc_icon)

        fc_title = QLabel("FACE LOGIN")
        fc_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        fc_title.setStyleSheet("color: #00ffff;")
        fc_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fc_layout.addWidget(fc_title)

        fc_desc = QLabel("Webcam Facial Recognition\nCamera activates on selection")
        fc_desc.setFont(QFont("Segoe UI", 9))
        fc_desc.setStyleSheet("color: #94a3b8;")
        fc_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fc_layout.addWidget(fc_desc)

        face_btn = QPushButton("📷 ACCESS WITH FACE")
        face_btn.setObjectName("primary_face")
        face_btn.clicked.connect(self._launch_face_auth)
        fc_layout.addWidget(face_btn)

        cards_layout.addWidget(face_card)

        # CARD 2: VOICE LOGIN
        voice_card = QFrame()
        voice_card.setObjectName("card_voice")
        vc_layout = QVBoxLayout(voice_card)
        vc_layout.setSpacing(12)

        vc_badge = QLabel("[ SPEAKER VERIFICATION ]")
        vc_badge.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        vc_badge.setStyleSheet("color: #00ff88;")
        vc_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vc_layout.addWidget(vc_badge)

        vc_icon = QLabel("🎤")
        vc_icon.setFont(QFont("Segoe UI", 38))
        vc_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vc_layout.addWidget(vc_icon)

        vc_title = QLabel("VOICE LOGIN")
        vc_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        vc_title.setStyleSheet("color: #00ff88;")
        vc_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vc_layout.addWidget(vc_title)

        vc_desc = QLabel("Biometric Voice Verification\nMicrophone acoustic matching")
        vc_desc.setFont(QFont("Segoe UI", 9))
        vc_desc.setStyleSheet("color: #94a3b8;")
        vc_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vc_layout.addWidget(vc_desc)

        voice_btn = QPushButton("🎙️ ACCESS WITH VOICE")
        voice_btn.setObjectName("primary_voice")
        voice_btn.clicked.connect(self._launch_voice_auth)
        vc_layout.addWidget(voice_btn)

        cards_layout.addWidget(voice_card)

        layout.addLayout(cards_layout)

        # Bottom Bar: Registration & Exit
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)
        
        reg_btn = QPushButton("📝 REGISTER BIOMETRICS")
        reg_btn.setObjectName("reg_btn")
        reg_btn.clicked.connect(self._launch_registration_prompt)
        bottom_layout.addWidget(reg_btn)

        exit_btn = QPushButton("❌ EXIT SYSTEM")
        exit_btn.setObjectName("exit_btn")
        exit_btn.clicked.connect(self.reject)
        bottom_layout.addWidget(exit_btn)

        layout.addLayout(bottom_layout)

    def _launch_face_auth(self):
        """Launches Face Recognition Dialog (Webcam turns ON here)."""
        self.hide()
        dlg = FaceAuthDialog()
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.authenticated_user = dlg.authenticated_user or "Authorized User"
            self.accept()
        else:
            self.show()

    def _launch_voice_auth(self):
        """Launches Biometric Voice Recognition Dialog."""
        self.hide()
        dlg = VoiceAuthDialog()
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.authenticated_user = dlg.authenticated_user or "Authorized User"
            self.accept()
        else:
            self.show()

    def _launch_registration_prompt(self):
        """Prompts user to choose Face or Voice enrollment."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Register Biometrics")
        msg_box.setText("Choose Biometric Enrollment Type:")
        
        face_reg_btn = msg_box.addButton("👤 Register Face", QMessageBox.ButtonRole.ActionRole)
        voice_reg_btn = msg_box.addButton("🎤 Register Voice", QMessageBox.ButtonRole.ActionRole)
        cancel_btn = msg_box.addButton(QMessageBox.StandardButton.Cancel)

        msg_box.exec()

        if msg_box.clickedButton() == face_reg_btn:
            self.hide()
            dlg = FaceAuthDialog()
            dlg.exec()
            self._update_status_banner()
            self.show()
        elif msg_box.clickedButton() == voice_reg_btn:
            self.hide()
            dlg = VoiceAuthDialog()
            dlg.exec()
            self._update_status_banner()
            self.show()

    def _update_status_banner(self):
        """Refreshes profile counts after registration."""
        faces_count = len(load_face_encodings())
        voices_count = len(load_voice_encodings())
        print(f"[AUTH PORTAL] Profiles updated: {faces_count} faces, {voices_count} voices.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    portal = BiometricAuthPortal()
    portal.show()
    sys.exit(app.exec())
