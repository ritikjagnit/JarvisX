import os
import sys
import json
import time
import random
import cv2
import numpy as np
from datetime import datetime

from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QImage, QPixmap, QFont, QColor, QPainter, QPen, QBrush, QLinearGradient, QRadialGradient
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QLineEdit,
    QProgressBar, QFrame, QMessageBox, QFileDialog, QGraphicsDropShadowEffect, QApplication
)

DOSSIER_DIR = os.path.join("jarvis_data", "dossiers")
PROFILE_FILE = os.path.join(DOSSIER_DIR, "dossier_profiles.json")

def ensure_dossier_dir():
    os.makedirs(DOSSIER_DIR, exist_ok=True)


# ----------------- DYNAMIC DOSSIER GENERATOR -----------------

def load_custom_dossiers():
    ensure_dossier_dir()
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_custom_dossier(name, data):
    ensure_dossier_dir()
    profiles = load_custom_dossiers()
    profiles[name.strip().lower()] = data
    try:
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=4)
        return True
    except Exception as e:
        print(f"[DOSSIER SAVE ERROR] {e}")
        return False


def generate_ai_dossier(name, target_role="Unknown Subject"):
    """
    Generates a futuristic, creative, and highly detailed 'Astro Profile' dossier profile using Gemini AI.
    Falls back to a rich deterministic local astrological engine if quota/offline occurs.
    """
    # Check custom saved profiles first
    profiles = load_custom_dossiers()
    name_key = name.strip().lower()
    if name_key in profiles:
        return profiles[name_key]

    try:
        import google.generativeai as genai
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            model_candidates = [
                "gemini-2.0-flash", 
                "gemini-2.0-flash-lite", 
                "gemini-2.0-flash-lite-preview-02-05",
                "gemini-1.5-flash-002",
                "gemini-1.5-flash-001"
            ]

            prompt = f"""
            You are Intelligent AI, an elite futuristic AI intelligence and Astrological Cyber-Architect.
            Generate an IN-DEPTH, highly detailed, authentic yet futuristic 'Astro Profile' (Cyber Security & Astrological Dossier) for a subject named "{name}" (Target Role / Context: "{target_role}").

            Return a valid JSON object with the following exact keys:
            - "subject_name": "{name}"
            - "classification": Futuristic title/role (e.g. "Cybernetic Architect", "Quantum Netrunner", "AI Arch-Sorcerer")
            - "rashi_alignment": Astrological Rashi & Nakshatra (e.g. "Simha (Leo) — Purva Phalguni Nakshatra")
            - "lucky_number": Lucky numbers (e.g. "7 & 21")
            - "element_color": Element & Power Color (e.g. "Agni (Fire) | Cyber Cyan")
            - "power_level": Integer (50 to 100) representing their technical/power index
            - "behavioral_trait": Short 4-word primary personality trait
            - "strengths": Array of 4 detailed technical and personal superpowers
            - "weaknesses": Array of 4 humorous vulnerabilities or quirks
            - "dosha_analysis": 1-sentence astrological & technical flaw (e.g. "Rahu Mahadasha causing occasional syntax errors in production")
            - "destiny": 3-sentence detailed destiny prediction and Vedic/Cyber remedy (Upay)
            """

            for model_name in model_candidates:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    text_resp = response.text.strip()
                    if "```json" in text_resp:
                        text_resp = text_resp.split("```json")[1].split("```")[0].strip()
                    elif "```" in text_resp:
                        text_resp = text_resp.split("```")[1].split("```")[0].strip()

                    res_dict = json.loads(text_resp)
                    print(f"[DOSSIER SUCCESS] Generated comprehensive Astro Profile with Gemini model: {model_name}")
                    return res_dict
                except Exception as m_err:
                    print(f"[GEMINI DOSSIER TRY] {model_name} failed: {m_err}")
                    continue
    except Exception as e:
        print(f"[DOSSIER NOTICE] Switching to local dynamic dossier engine: {e}")

    # Rich Deterministic Astrological Astro Profile Engine (Offline / Rate Limit Fallback)
    name_clean = name.strip() or "Subject"
    seed = sum(ord(c) for c in name_clean)
    
    rashis = ["Mesha (Aries)", "Vrishabha (Taurus)", "Mithuna (Gemini)", "Karka (Cancer)", "Simha (Leo)", "Kanya (Virgo)", "Tula (Libra)", "Vrishchika (Scorpio)", "Dhanu (Sagittarius)", "Makara (Capricorn)", "Kumbha (Aquarius)", "Meena (Pisces)"]
    nakshatras = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Visakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
    
    rashi = rashis[seed % len(rashis)]
    nakshatra = nakshatras[(seed * 7) % len(nakshatras)]

    classes = [
        "Cybernetic Arch-Architect", "Quantum Netrunner", "Technomancer Supreme", 
        "AI Core Specialist", "Matrix Infiltrator", "Data Arch-Druid", "Neural Nexus Commander"
    ]
    classification = classes[seed % len(classes)]

    traits = [
        "Unpredictable Visionary & Code Catalyst", "Logic-Driven Strategic Thinker", 
        "Hyper-Focused Neural Architect", "Chaos-Resistant System Optimizer"
    ]
    trait = traits[(seed + 3) % len(traits)]

    power = min(100, max(68, 72 + (seed % 28)))

    strengths = [
        f"Shubh Grah Alignment in 10th House: Exceptional mastery over multi-threaded neural architectures.",
        f"Intuitive Bug Shield: Can spot critical production vulnerabilities and race conditions before compilation.",
        f"High Cognitive Bandwidth: Analyzes complex multi-layered system architectures with zero mental fatigue.",
        f"Leadership Radiance: Calm aura that stabilizes high-stress deployment failures and server crashes."
    ]

    weaknesses = [
        "Rahu Influence: Extreme vulnerability to high network latency (>100ms) causing mild frustration.",
        "Dark Mode Dependency: Cannot write or review code in bright or light-themed developer environments.",
        "Perfectionist Dosha: Tendency to refactor perfectly working 100% stable modules for aesthetic elegance.",
        "Caffeine Coupling: System energy drops by 40% if espresso or hot tea intake is delayed."
    ]

    dosha = f"Shani Dev in 5th House of Event Loops: Temporary delay in complex async function execution, resolved by patience."
    destiny = f"{name_clean} is predestined by cosmic planetary alignment to architect a game-changing AI platform. Your Nakshatra ({nakshatra}) grants unmatched analytical supremacy over complex problems. Remedy (Upay): Maintain dark mode themes, drink green tea, and execute 'python main.py' daily."

    return {
        "subject_name": name_clean,
        "classification": classification,
        "rashi_alignment": f"{rashi} — {nakshatra} Nakshatra",
        "lucky_number": f"{((seed * 7) % 9) + 1} & {((seed * 3) % 9) + 2}",
        "element_color": "Tejas (Fire) | Holographic Cyan",
        "power_level": power,
        "behavioral_trait": trait,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "dosha_analysis": dosha,
        "destiny": destiny
    }


# ----------------- PDF EXPORTER -----------------

def export_dossier_pdf(dossier_data):
    """
    Exports a beautiful, themed PDF Dossier Report.
    """
    ensure_dossier_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name_sanitized = "".join(c for c in dossier_data.get("subject_name", "Subject") if c.isalnum())
    pdf_path = os.path.join(DOSSIER_DIR, f"Dossier_{name_sanitized}_{timestamp}.pdf")

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, HRFlowable, Spacer

        pdf_doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor("#0f172a"), spaceAfter=4)
        sub_style = ParagraphStyle('Sub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#0284c7"), spaceAfter=10)
        h1_style = ParagraphStyle('H1', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#0f172a"), spaceBefore=10, spaceAfter=4)
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13.5, textColor=colors.HexColor("#334155"), spaceAfter=4)
        bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor("#334155"), leftIndent=15, spaceAfter=3)

        story = []
        story.append(Paragraph("INTELLIGENT AI — SECURITY FILES & IDENTITY DOSSIER", title_style))
        story.append(Paragraph(f"Subject: {dossier_data.get('subject_name')}  |  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", sub_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=10))

        story.append(Paragraph("Subject Metadata", h1_style))
        story.append(Paragraph(f"<b>Classification:</b> {dossier_data.get('classification')}", body_style))
        story.append(Paragraph(f"<b>Power/Technical Index:</b> {dossier_data.get('power_level')}/100", body_style))
        story.append(Paragraph(f"<b>Primary Trait:</b> {dossier_data.get('behavioral_trait')}", body_style))

        story.append(Paragraph("Dossier Strengths & Highlights", h1_style))
        for item in dossier_data.get("strengths", []):
            story.append(Paragraph(f"• {item}", bullet_style))

        story.append(Paragraph("Vulnerabilities & Weaknesses", h1_style))
        for item in dossier_data.get("weaknesses", []):
            story.append(Paragraph(f"• {item}", bullet_style))

        story.append(Paragraph("Astro Profile / Future Forecast", h1_style))
        story.append(Paragraph(dossier_data.get("destiny", ""), body_style))

        pdf_doc.build(story)
        print(f"[DOSSIER PDF] Saved successfully to {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"[DOSSIER PDF ERROR] {e}")
        return None


# ----------------- CAMERA RUNNER THREAD -----------------

class CameraScannerThread(QThread):
    """
    Background worker frame processor for face tracking and camera display.
    """
    frame_ready = pyqtSignal(QImage, bool) # processed_qimage, face_detected

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self.running = False
        
        # Load local face detector Haar Cascade safely
        self.face_cascade = None
        try:
            if hasattr(cv2, 'CascadeClassifier'):
                cascade_path = getattr(cv2.data, 'haarcascades', '') + 'haarcascade_frontalface_default.xml'
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
        except Exception as e:
            print(f"[FACE DOSSIER NOTICE] CascadeClassifier not available: {e}")

    def run(self):
        self.running = True
        cap = cv2.VideoCapture(self.camera_index)
        
        # Optimize camera resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        # Pulse angle for scanning HUD animations
        hud_angle = 0

        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.03)
                continue

            # Mirror image for natural view
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces with multiple fallbacks
            faces = []
            if self.face_cascade is not None:
                try:
                    detected = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
                    if len(detected) > 0:
                        faces = detected
                except Exception:
                    pass

            if len(faces) == 0:
                try:
                    import face_recognition
                    locs = face_recognition.face_locations(frame)
                    for (top, right, bottom, left) in locs:
                        faces.append((left, top, right - left, bottom - top))
                except Exception:
                    pass

            if len(faces) == 0:
                # Center Target Box Reticle Fallback
                h_f, w_f, _ = frame.shape
                cw, ch = int(w_f * 0.45), int(h_f * 0.55)
                cx, cy = int((w_f - cw) / 2), int((h_f - ch) / 2)
                faces = [(cx, cy, cw, ch)]

            face_detected = True

            hud_angle += 5
            pulse_val = abs(np.sin(np.radians(hud_angle)))

            # Draw Cyberpunk Scanner HUD over frame
            for (x, y, w, h) in faces:
                # 1. Bounding target frame corners
                length = int(w * 0.25)
                color = (0, 255, 0) # Green for matched scan
                
                # Top-Left Corner
                cv2.line(frame, (x, y), (x + length, y), color, 2)
                cv2.line(frame, (x, y), (x, y + length), color, 2)
                
                # Top-Right Corner
                cv2.line(frame, (x + w, y), (x + w - length, y), color, 2)
                cv2.line(frame, (x + w, y), (x + w, y + length), color, 2)
                
                # Bottom-Left Corner
                cv2.line(frame, (x, y + h), (x + length, y + h), color, 2)
                cv2.line(frame, (x, y + h), (x, y + h - length), color, 2)
                
                # Bottom-Right Corner
                cv2.line(frame, (x + w, y + h), (x + w - length, y + h), color, 2)
                cv2.line(frame, (x + w, y + h), (x + w, y + h - length), color, 2)

                # 2. Scanning horizontal HUD line
                scan_y = int(y + pulse_val * h)
                cv2.line(frame, (x + 5, scan_y), (x + w - 5, scan_y), (0, 255, 255), 1)

                # 3. Label overlay
                cv2.putText(frame, "ANALYZING SUBJECT...", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

            # Convert BGR frame to QImage for QLabel display
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h_h, w_w, ch = rgb_image.shape
            bytes_per_line = ch * w_w
            q_image = QImage(rgb_image.data, w_w, h_h, bytes_per_line, QImage.Format.Format_RGB888)
            
            self.frame_ready.emit(q_image, face_detected)
            
            # Limit processing speed to save CPU cycles
            time.sleep(0.04)

        cap.release()

    def stop(self):
        self.running = False
        self.wait()


# ----------------- DOSSIIER DIALOG UI -----------------

class FaceDossierDialog(QDialog):
    """
    Cyberpunk UI Dialog for AI Face Scanning and Janam-Kundli Profile Generation.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("INTELLIGENT AI SECURITY HUB - AI IDENTITY & FACE DOSSIER SCANNER")
        self.resize(1100, 720)
        ensure_dossier_dir()

        self.setStyleSheet("""
            QDialog {
                background: #020617;
                border: 2px solid #00ffff;
                border-radius: 18px;
            }
            QLabel { color: #ffffff; }
            QPushButton {
                background: rgba(0, 255, 255, 0.15);
                color: #00ffff;
                border: 1.5px solid #00ffff;
                border-radius: 8px;
                padding: 10px 18px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(0, 255, 255, 0.4);
                color: #ffffff;
                border-color: #ffffff;
            }
            QPushButton#action_btn {
                background: rgba(0, 255, 136, 0.2);
                color: #00ff88;
                border-color: #00ff88;
            }
            QPushButton#action_btn:hover {
                background: rgba(0, 255, 136, 0.5);
                color: #ffffff;
            }
            QLineEdit {
                background: #090d16;
                color: #00ffff;
                border: 1px solid #0066ff;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QTextEdit {
                background: #090d16;
                color: #ffffff;
                border: 1px solid #0066ff;
                border-radius: 8px;
                font-family: Consolas;
                font-size: 11px;
                padding: 10px;
            }
            QProgressBar {
                border: 1.5px solid #00ffff;
                border-radius: 6px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                font-size: 12px;
                background: #090d16;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00ffff, stop:1 #00ff88);
                border-radius: 5px;
            }
        """)

        try:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(30)
            shadow.setColor(QColor(0, 255, 255, 150))
            shadow.setOffset(0, 0)
            self.setGraphicsEffect(shadow)
        except Exception:
            pass

        self.camera_thread = None
        self.current_dossier = None
        self.face_detected_now = False

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        title = QLabel("JARVISX AI IDENTITY SCANNER & CYBER DOSSIER GENERATOR")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Main Layout split: Left (Camera) vs Right (Dossier Panel)
        main_box = QHBoxLayout()

        # Left Column: Camera Preview
        cam_panel = QVBoxLayout()
        self.cam_screen = QLabel()
        self.cam_screen.setFixedSize(540, 420)
        self.cam_screen.setStyleSheet("background-color: #090d16; border: 2px solid #0066ff; border-radius: 8px;")
        self.cam_screen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cam_screen.setText("CAMERA PREVIEW ONLINE")
        cam_panel.addWidget(self.cam_screen)

        # Scanner Buttons
        scan_bar = QHBoxLayout()
        self.toggle_cam_btn = QPushButton("📷 START CAMERA")
        self.toggle_cam_btn.clicked.connect(self._toggle_camera)
        scan_bar.addWidget(self.toggle_cam_btn)

        self.scan_btn = QPushButton("🔍 PERFORM DOCK SCAN")
        self.scan_btn.setObjectName("action_btn")
        self.scan_btn.setEnabled(False)
        self.scan_btn.clicked.connect(self._perform_scan)
        scan_bar.addWidget(self.scan_btn)

        cam_panel.addLayout(scan_bar)
        main_box.addLayout(cam_panel)

        # Right Column: Dossier Output Panel
        dossier_panel = QVBoxLayout()
        dossier_panel.setSpacing(10)

        # Name Input
        name_bar = QHBoxLayout()
        n_lbl = QLabel("Subject Name/Alias:")
        n_lbl.setStyleSheet("color: #00ffff; font-weight: bold;")
        name_bar.addWidget(n_lbl)

        self.name_input = QLineEdit()
        self.name_input.setText("Shravani")
        name_bar.addWidget(self.name_input)
        dossier_panel.addLayout(name_bar)

        # Target Role
        role_bar = QHBoxLayout()
        r_lbl = QLabel("Target / Description:")
        r_lbl.setStyleSheet("color: #00ffff; font-weight: bold;")
        role_bar.addWidget(r_lbl)

        self.role_input = QLineEdit()
        self.role_input.setText("Creator & Head AI Architect")
        role_bar.addWidget(self.role_input)
        dossier_panel.addLayout(role_bar)

        # Dossier Text viewer
        self.dossier_view = QTextEdit()
        self.dossier_view.setStyleSheet("color: #00ff88;")
        self.dossier_view.setPlaceholderText("Dossier reports and AI Identity details will appear here after performing a face scan...")
        dossier_panel.addWidget(self.dossier_view)

        # Power Index progress bar
        self.power_lbl = QLabel("POWER/TECHNICAL INDEX:")
        self.power_lbl.setStyleSheet("color: #00ffff; font-weight: bold;")
        dossier_panel.addWidget(self.power_lbl)

        self.power_bar = QProgressBar()
        self.power_bar.setValue(0)
        dossier_panel.addWidget(self.power_bar)

        main_box.addLayout(dossier_panel)

        layout.addLayout(main_box)

        # Bottom Status Bar
        bottom_bar = QHBoxLayout()
        self.status_label = QLabel("Status: Click 'START CAMERA' to begin target recognition.")
        self.status_label.setStyleSheet("color: #94a3b8;")
        bottom_bar.addWidget(self.status_label)

        self.save_btn = QPushButton("💾 SAVE PROFILE DETAILS")
        self.save_btn.clicked.connect(self._save_profile_details)
        self.save_btn.setEnabled(False)
        bottom_bar.addWidget(self.save_btn)

        self.pdf_btn = QPushButton("📄 EXPORT DOSSIER (PDF)")
        self.pdf_btn.clicked.connect(self._export_pdf)
        self.pdf_btn.setEnabled(False)
        bottom_bar.addWidget(self.pdf_btn)

        self.folder_btn = QPushButton("📁 OPEN DOSSIERS")
        self.folder_btn.clicked.connect(self._open_folder)
        bottom_bar.addWidget(self.folder_btn)

        layout.addLayout(bottom_bar)

    def _toggle_camera(self):
        if self.camera_thread and self.camera_thread.running:
            self.camera_thread.stop()
            self.camera_thread = None
            self.toggle_cam_btn.setText("📷 START CAMERA")
            self.scan_btn.setEnabled(False)
            self.cam_screen.clear()
            self.cam_screen.setText("CAMERA PREVIEW ONLINE")
        else:
            self.toggle_cam_btn.setText("⏹️ STOP CAMERA")
            self.camera_thread = CameraScannerThread(camera_index=0)
            self.camera_thread.frame_ready.connect(self._update_camera_frame)
            self.camera_thread.start()

    def _update_camera_frame(self, q_img, face_detected):
        self.cam_screen.setPixmap(QPixmap.fromImage(q_img).scaled(
            self.cam_screen.width(), self.cam_screen.height(),
            Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        ))
        self.face_detected_now = face_detected
        self.scan_btn.setEnabled(face_detected)
        
        if face_detected:
            self.status_label.setText("Status: 🟢 Target Locked. Click 'PERFORM DOCK SCAN' to compile bio.")
        else:
            self.status_label.setText("Status: 🔴 Scanning... Align face inside camera feed.")

    def _perform_scan(self):
        name = self.name_input.text().strip() or "Subject"
        target_role = self.role_input.text().strip() or "Unknown Specialist"
        
        self.status_label.setText("Status: 🤖 Retrieving security dossier details...")
        QApplication.processEvents()

        dossier = generate_ai_dossier(name, target_role=target_role)
        self.current_dossier = dossier

        power = dossier.get("power_level", 75)
        self.power_bar.setValue(power)
        self.power_lbl.setText(f"POWER/TECHNICAL INDEX: {power}/100")

        d_text = (
            f"=== 📜 CYBER DOSSIER & PROFILE: {dossier.get('subject_name', name).upper()} ===\n"
            f"🔮 ALIGNMENT: {dossier.get('rashi_alignment', 'Simha (Leo)')}\n"
            f"✨ ACCESS CODE: {dossier.get('lucky_number', '7 & 21')}  |  ELEMENT: {dossier.get('element_color', 'Agni')}\n"
            f"🚀 CLASSIFICATION: {dossier.get('classification', '')}\n"
            f"🧠 PRIMARY TRAIT: {dossier.get('behavioral_trait', '')}\n\n"
            f"💪 STRENGTHS & SUPERPOWERS:\n" + "\n".join([f"• {item}" for item in dossier.get("strengths", [])]) + "\n\n"
            f"⚠️ VULNERABILITIES & WEAKNESSES:\n" + "\n".join([f"• {item}" for item in dossier.get("weaknesses", [])]) + "\n\n"
            f"🪐 RISK & SECURITY ANALYSIS:\n• {dossier.get('dosha_analysis', '')}\n\n"
            f"🔮 STRATEGIC FORECAST:\n{dossier.get('destiny', '')}"
        )
        self.dossier_view.setPlainText(d_text)

        self.save_btn.setEnabled(True)
        self.pdf_btn.setEnabled(True)
        self.status_label.setText("Status: ✨ Authentic Cyber Dossier & Bio Profile Compiled!")

        # Speak overview
        try:
            from voice_engine import speak
            speak(f"Identity scan complete. Target classification, {dossier.get('classification')}. Primary trait, {dossier.get('behavioral_trait')}.")
        except Exception:
            pass

    def _save_profile_details(self):
        if not self.current_dossier:
            return
        name = self.name_input.text().strip()
        if save_custom_dossier(name, self.current_dossier):
            QMessageBox.information(self, "Profile Saved", f"Identity details for '{name}' saved successfully in local dossier database.")

    def _export_pdf(self):
        if not self.current_dossier:
            return
        pdf_path = export_dossier_pdf(self.current_dossier)
        if pdf_path:
            QMessageBox.information(self, "Dossier Exported", f"Security Dossier saved successfully:\n{os.path.basename(pdf_path)}")

    def _open_folder(self):
        if os.path.exists(DOSSIER_DIR):
            os.startfile(DOSSIER_DIR)

    def closeEvent(self, event):
        if self.camera_thread and self.camera_thread.running:
            self.camera_thread.stop()
        event.accept()
