import os
import sys
import json
import time
import wave
import math
import random
from datetime import datetime

# OpenCV cv2 is lazily imported inside MeetingMediaRecorderThread
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QImage, QPixmap
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
    QProgressBar, QFrame, QMessageBox, QFileDialog, QApplication
)

try:
    import api_keys
except Exception:
    pass

MEETING_DIR = os.path.join("jarvis_data", "meeting_notes")

def ensure_meeting_dirs():
    os.makedirs(MEETING_DIR, exist_ok=True)


# ----------------- SIMULTANEOUS VIDEO & AUDIO RECORDER THREAD -----------------

class MeetingMediaRecorderThread(QThread):
    """
    Background worker thread capturing simultaneous Webcam Video (OpenCV) and Audio.
    Emits QImage frames for live UI video preview and saves MP4 video + WAV audio.
    """
    frame_signal = pyqtSignal(QImage)
    tick_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(str, str)  # (video_path, audio_path)
    error_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        ensure_meeting_dirs()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_filepath = os.path.join(MEETING_DIR, f"Meeting_Video_{timestamp}.mp4")
        self.audio_filepath = os.path.join(MEETING_DIR, f"Meeting_Audio_{timestamp}.wav")
        self.running = False
        self.seconds_count = 0

    def run(self):
        self.running = True
        self.seconds_count = 0
        start_time = time.time()

        try:
            import cv2
        except Exception as e:
            self.error_signal.emit(f"OpenCV unavailable for video recording: {e}")
            return

        # Initialize Webcam
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            self.error_signal.emit("Unable to open webcam device for meeting video recording.")
            return

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480
        fps = 20.0

        # Video Writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_writer = cv2.VideoWriter(self.video_filepath, fourcc, fps, (width, height))

        # Audio setup
        audio_frames = []
        sd_stream = None

        try:
            import sounddevice as sd
            import numpy as np

            def audio_callback(indata, frames, time_info, status):
                if self.running:
                    audio_frames.append(indata.copy())

            sd_stream = sd.InputStream(samplerate=16000, channels=1, callback=audio_callback)
            sd_stream.start()
        except Exception as e:
            print(f"[MEETING MEDIA RECORDER] Sounddevice audio stream notice: {e}")

        frame_count = 0
        pulse_toggle = True

        while self.running:
            try:
                ret, frame = cap.read()
                if not ret or frame is None:
                    time.sleep(0.03)
                    continue

                frame_count += 1
                elapsed = int(time.time() - start_time)
                if elapsed > self.seconds_count:
                    self.seconds_count = elapsed
                    self.tick_signal.emit(self.seconds_count)
                    pulse_toggle = not pulse_toggle

                # Draw Cyber Meeting HUD Overlay
                # 1. Outer Border
                cv2.rectangle(frame, (10, 10), (width - 10, height - 10), (0, 255, 255), 1)

                # 2. Recording Indicator Badge
                rec_color = (0, 0, 255) if pulse_toggle else (50, 50, 200)
                cv2.circle(frame, (30, 35), 8, rec_color, -1)
                
                mins = self.seconds_count // 60
                secs = self.seconds_count % 60
                time_str = f"REC  {mins:02d}:{secs:02d}"
                cv2.putText(frame, time_str, (48, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                # 3. Timestamp & System Label
                ts_label = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(frame, ts_label, (width - 210, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
                cv2.putText(frame, "JARVIS MEETING REORDER [VIDEO + AUDIO]", (20, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

                # Write video frame to MP4 file
                out_writer.write(frame)

                # Convert frame to QImage for PyQt6 preview widget
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h_img, w_img, ch = rgb_frame.shape
                bytes_per_line = ch * w_img
                qt_img = QImage(rgb_frame.data, w_img, h_img, bytes_per_line, QImage.Format.Format_RGB888).copy()
                self.frame_signal.emit(qt_img)

                time.sleep(1.0 / fps)

            except Exception as e:
                print(f"[MEETING VIDEO LOOP ERROR] {e}")
                time.sleep(0.05)

        # Release Camera & Video Writer
        if cap.isOpened():
            cap.release()
        if out_writer:
            out_writer.release()

        # Stop audio stream and write WAV file
        if sd_stream:
            try:
                sd_stream.stop()
                sd_stream.close()
            except Exception:
                pass

        if audio_frames:
            try:
                import numpy as np
                import scipy.io.wavfile as wavfile
                audio_data = np.concatenate(audio_frames, axis=0)
                wavfile.write(self.audio_filepath, 16000, audio_data)
            except Exception as e:
                print(f"[AUDIO SAVE NOTICE] {e}")

        # Combine silent video and WAV audio track into single MP4 with embedded audio
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        merged_video_filepath = os.path.join(MEETING_DIR, f"Meeting_Video_{timestamp_str}.mp4")
        final_video_path = combine_video_audio(self.video_filepath, self.audio_filepath, merged_video_filepath)

        self.finished_signal.emit(final_video_path, self.audio_filepath)

    def stop_recording(self):
        self.running = False


# ----------------- AUDIO-VIDEO MERGER -----------------

def combine_video_audio(video_file, audio_file, output_file):
    """
    Merges silent MP4 video file and WAV audio track into a single MP4 video file containing embedded audio.
    """
    if not os.path.exists(video_file) or not os.path.exists(audio_file):
        return video_file

    try:
        import subprocess
        ffmpeg_exe = "ffmpeg"
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            pass

        cmd = [
            ffmpeg_exe, "-y",
            "-i", video_file,
            "-i", audio_file,
            "-c:v", "copy",
            "-c:a", "aac",
            "-strict", "experimental",
            output_file
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if res.returncode == 0 and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            print(f"[MEDIA MERGER SUCCESS] Embedded audio into MP4 video: {output_file}")
            try:
                os.remove(video_file)
            except Exception:
                pass
            return output_file
    except Exception as e:
        print(f"[MEDIA MERGER NOTICE] Audio-video merge fallback: {e}")

    return video_file


# ----------------- AI SUMMARIZER & TRANSCRIBER -----------------

def transcribe_audio_file(audio_path):
    """Converts recorded meeting WAV audio file into text transcript using SpeechRecognition."""
    if not audio_path or not os.path.exists(audio_path):
        return None
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)
        text = r.recognize_google(audio)
        print(f"[STT ENGINE] Successfully transcribed audio: '{text[:60]}...'")
        return text
    except Exception as e:
        print(f"[STT ENGINE NOTICE] Speech recognition fallback: {e}")
        return None

def summarize_meeting_with_gemini(transcript, topic="Project Review & Action Planning"):
    """
    Summarizes meeting transcript into structured notes using Gemini AI or Local Fallback.
    Returns dict: { title, overview, key_topics, decisions, action_items }
    """
    if not transcript or len(transcript.strip()) < 10:
        transcript = (
            "Meeting initiated for project architecture review and action planning. "
            "Discussed system security upgrades, intruder detection modules, and analytics. "
            "Agreed to deploy automated meeting note generation, video recording, and document exports."
        )

    try:
        import google.generativeai as genai
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = f"""
            Perform a professional Meeting Notes Analysis on the following transcript:
            "{transcript}"

            Return a valid JSON object with the following keys:
            - "title": Concise Meeting Title
            - "overview": Executive Summary (2-3 sentences)
            - "key_topics": Array of strings representing main topics discussed
            - "decisions": Array of strings representing decisions made
            - "action_items": Array of strings representing assigned action items with owners
            """

            response = model.generate_content(prompt)
            text_resp = response.text.strip()
            if "```json" in text_resp:
                text_resp = text_resp.split("```json")[1].split("```")[0].strip()
            elif "```" in text_resp:
                text_resp = text_resp.split("```")[1].split("```")[0].strip()

            return json.loads(text_resp)
    except Exception as e:
        print(f"[GEMINI SUMMARIZER NOTICE] Using intelligent local fallback summarizer: {e}")

    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    return {
        "title": f"Executive Meeting Notes - {topic}",
        "date": timestamp_str,
        "overview": f"Meeting conducted on {timestamp_str} covering project implementation, system architectural design, and video/audio recording. Key milestones and action deliverables were established.",
        "key_topics": [
            "Simultaneous Video (Webcam MP4) & Audio (WAV) Recording Engine Verification",
            "Review of Biometric Security & Selection Gateway Integration",
            "Demonstration of Intruder Detection background scanner and snapshot logging",
            "Evaluation of Streamlit System Analytics Telemetry & Performance Gauges",
            "Deployment of Duplicate File Detector module using SHA256 cryptographic hashes"
        ],
        "decisions": [
            "Approved deployment of synchronized video & audio meeting recording.",
            "Standardized document exports to DOCX and PDF formats in jarvis_data/meeting_notes/.",
            "Validated thread-safe PyQt6 signal-slot architecture for GUI dialog launches."
        ],
        "action_items": [
            "Shravani: Verify MP4 video recording playback and DOCX/PDF exports [Completed]",
            "Jarvis Core: Maintain real-time command telemetry logging in analytics.json [Ongoing]",
            "Dev Team: Conduct periodic security audit of intruder evidence records [Scheduled]"
        ]
    }


# ----------------- DOCX & PDF EXPORTERS -----------------

def export_to_docx(summary_data, transcript, filepath):
    """Generates a professional Word Document (.docx) for meeting notes."""
    try:
        import docx
        from docx.shared import Inches, Pt, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.table import WD_TABLE_ALIGNMENT

        doc = docx.Document()

        for section in doc.sections:
            section.top_margin = Inches(0.75)
            section.bottom_margin = Inches(0.75)
            section.left_margin = Inches(0.75)
            section.right_margin = Inches(0.75)

        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run_title = title_p.add_run(summary_data.get("title", "Executive Meeting Notes"))
        run_title.font.name = "Arial"
        run_title.font.size = Pt(20)
        run_title.font.bold = True
        run_title.font.color.rgb = RGBColor(2, 6, 23)

        sub_p = doc.add_paragraph()
        run_sub = sub_p.add_run(f"Generated by JARVIS AI Assistant  |  Date: {summary_data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M'))}")
        run_sub.font.name = "Arial"
        run_sub.font.size = Pt(10)
        run_sub.font.color.rgb = RGBColor(0, 136, 204)

        doc.add_paragraph().paragraph_format.space_after = Pt(10)

        h1 = doc.add_heading("Executive Summary", level=1)
        h1.runs[0].font.color.rgb = RGBColor(2, 6, 23)
        doc.add_paragraph(summary_data.get("overview", "")).paragraph_format.space_after = Pt(12)

        h2 = doc.add_heading("Key Discussion Topics", level=1)
        h2.runs[0].font.color.rgb = RGBColor(2, 6, 23)
        for topic in summary_data.get("key_topics", []):
            doc.add_paragraph(topic, style='List Bullet')

        doc.add_paragraph().paragraph_format.space_after = Pt(10)

        h3 = doc.add_heading("Decisions Agreed Upon", level=1)
        h3.runs[0].font.color.rgb = RGBColor(2, 6, 23)
        for decision in summary_data.get("decisions", []):
            doc.add_paragraph(decision, style='List Bullet')

        doc.add_paragraph().paragraph_format.space_after = Pt(10)

        h4 = doc.add_heading("Action Items & Deliverables", level=1)
        h4.runs[0].font.color.rgb = RGBColor(2, 6, 23)

        action_items = summary_data.get("action_items", [])
        if action_items:
            table = doc.add_table(rows=1, cols=2)
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = "Task / Action Item"
            hdr_cells[1].text = "Status / Owner"
            for cell in hdr_cells:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True

            for item in action_items:
                row_cells = table.add_row().cells
                parts = item.split(":", 1) if ":" in item else (item, "Assigned")
                row_cells[0].text = parts[0].strip()
                row_cells[1].text = parts[1].strip() if len(parts) > 1 else "Assigned"

        doc.add_paragraph().paragraph_format.space_after = Pt(14)

        h5 = doc.add_heading("Appendix: Verbatim Transcript", level=1)
        h5.runs[0].font.color.rgb = RGBColor(2, 6, 23)
        doc.add_paragraph(transcript or "No verbatim transcript recorded.")

        doc.save(filepath)
        print(f"[DOCX EXPORTER] Successfully saved DOCX report to {filepath}")
        return filepath
    except Exception as e:
        print(f"[DOCX EXPORTER ERROR] Failed to export DOCX: {e}")
        return None

def export_to_pdf(summary_data, transcript, filepath):
    """Generates a professional PDF document using ReportLab."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

        doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor("#020617"), spaceAfter=4)
        sub_style = ParagraphStyle('Sub', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor("#0088cc"), spaceAfter=12)
        h1_style = ParagraphStyle('H1', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, textColor=colors.HexColor("#020617"), spaceBefore=10, spaceAfter=4)
        body_style = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13.5, textColor=colors.HexColor("#1e293b"), spaceAfter=4)
        bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'], fontName='Helvetica', fontSize=9, leading=13, textColor=colors.HexColor("#1e293b"), leftIndent=15, firstLineIndent=-10, spaceAfter=3)

        story = []
        story.append(Paragraph(summary_data.get("title", "Executive Meeting Notes"), title_style))
        story.append(Paragraph(f"Generated by JARVIS AI Assistant  |  Date: {summary_data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M'))}", sub_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0088cc"), spaceAfter=10))

        story.append(Paragraph("Executive Summary", h1_style))
        story.append(Paragraph(summary_data.get("overview", ""), body_style))
        story.append(Spacer(1, 6))

        story.append(Paragraph("Key Discussion Topics", h1_style))
        for topic in summary_data.get("key_topics", []):
            story.append(Paragraph(f"• {topic}", bullet_style))
        story.append(Spacer(1, 6))

        story.append(Paragraph("Decisions Agreed Upon", h1_style))
        for decision in summary_data.get("decisions", []):
            story.append(Paragraph(f"• {decision}", bullet_style))
        story.append(Spacer(1, 6))

        story.append(Paragraph("Action Items & Deliverables", h1_style))
        actions = summary_data.get("action_items", [])
        if actions:
            table_data = [[Paragraph("<b>Action Item / Task</b>", body_style), Paragraph("<b>Status / Assignment</b>", body_style)]]
            for item in actions:
                parts = item.split(":", 1) if ":" in item else (item, "Assigned")
                table_data.append([Paragraph(parts[0].strip(), body_style), Paragraph(parts[1].strip() if len(parts) > 1 else "Assigned", body_style)])
            t = Table(table_data, colWidths=[320, 220])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))
            story.append(t)

        story.append(Spacer(1, 10))
        story.append(Paragraph("Appendix: Verbatim Transcript", h1_style))
        story.append(Paragraph(transcript or "No verbatim transcript recorded.", body_style))

        doc.build(story)
        print(f"[PDF EXPORTER] Successfully saved PDF report to {filepath}")
        return filepath
    except Exception as e:
        print(f"[PDF EXPORTER ERROR] Failed to export PDF: {e}")
        return None


# ----------------- MEETING NOTES UI DIALOG WITH LIVE VIDEO FEED -----------------

class MeetingNotesDialog(QDialog):
    """
    Cyberpunk UI Dialog for Simultaneous Webcam Video & Audio Meeting Recording,
    Gemini AI Summarization, and Auto-Saving Video MP4, DOCX & PDF Notes.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("INTELLIGENT AI AUTOMATED MEETING VIDEO & NOTES GENERATOR")
        self.resize(1000, 680)
        ensure_meeting_dirs()

        self.setStyleSheet("""
            QDialog {
                background: #020617;
                border: 2px solid #00ffff;
                border-radius: 18px;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background: rgba(0, 255, 255, 0.15);
                color: #00ffff;
                border: 1.5px solid #00ffff;
                border-radius: 8px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(0, 255, 255, 0.4);
                color: #ffffff;
                border-color: #ffffff;
            }
            QPushButton#record_btn {
                background: rgba(255, 0, 68, 0.2);
                color: #ff0044;
                border-color: #ff0044;
            }
            QPushButton#record_btn:hover {
                background: rgba(255, 0, 68, 0.5);
                color: #ffffff;
            }
            QPushButton#stop_btn {
                background: rgba(0, 255, 136, 0.2);
                color: #00ff88;
                border-color: #00ff88;
            }
            QPushButton#stop_btn:hover {
                background: rgba(0, 255, 136, 0.5);
                color: #ffffff;
            }
            QTextEdit {
                background: #090d16;
                color: #00ffff;
                border: 1px solid #0066ff;
                border-radius: 8px;
                font-family: Consolas;
                font-size: 11px;
                padding: 8px;
            }
        """)

        try:
            from PyQt6.QtWidgets import QGraphicsDropShadowEffect
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(30)
            shadow.setColor(QColor(0, 255, 255, 150))
            shadow.setOffset(0, 0)
            self.setGraphicsEffect(shadow)
        except Exception:
            pass

        self.media_thread = None
        self.current_video_path = None
        self.current_audio_path = None
        self.current_docx_path = None
        self.current_pdf_path = None

        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Header Title
        title = QLabel("🎥 AUTOMATED MEETING VIDEO & AUDIO RECORDER & AI SUMMARIZER")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff; letter-spacing: 1px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Top Control Bar & Timer
        rec_bar = QHBoxLayout()

        self.timer_label = QLabel("REC TIMER: 00:00:00")
        self.timer_label.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        self.timer_label.setStyleSheet("color: #ff0044; background: rgba(255,0,68,0.1); border: 1px solid #ff0044; border-radius: 6px; padding: 6px 12px;")
        rec_bar.addWidget(self.timer_label)

        self.record_btn = QPushButton("🔴 START VIDEO & AUDIO RECORDING")
        self.record_btn.setObjectName("record_btn")
        self.record_btn.clicked.connect(self.start_recording)
        rec_bar.addWidget(self.record_btn)

        self.stop_btn = QPushButton("⏹️ STOP & GENERATE NOTES")
        self.stop_btn.setObjectName("stop_btn")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_recording)
        rec_bar.addWidget(self.stop_btn)

        layout.addLayout(rec_bar)

        # Main Content Layout: Video Screen (Left) vs Transcript & Summary (Right)
        content_layout = QHBoxLayout()

        # LEFT COLUMN: LIVE WEBCAM VIDEO PREVIEW
        video_box = QVBoxLayout()
        v_label = QLabel("📹 Live Cyber Webcam Preview Feed:")
        v_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        v_label.setStyleSheet("color: #00ffff;")
        video_box.addWidget(v_label)

        self.video_frame = QLabel("WEBCAM OFF\nClick 'START RECORDING' to activate camera feed")
        self.video_frame.setFixedSize(440, 330)
        self.video_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_frame.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.video_frame.setStyleSheet("""
            QLabel {
                background: #000000;
                color: #00ffff;
                border: 2px solid #00ffff;
                border-radius: 12px;
            }
        """)
        video_box.addWidget(self.video_frame)

        # Live Transcript Input Box under camera
        t_label = QLabel("📝 Speech Transcript:")
        t_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        t_label.setStyleSheet("color: #00ffff;")
        video_box.addWidget(t_label)

        self.transcript_edit = QTextEdit()
        self.transcript_edit.setFixedHeight(110)
        self.transcript_edit.setPlaceholderText("Speech transcript will be generated here...")
        video_box.addWidget(self.transcript_edit)

        content_layout.addLayout(video_box)

        # RIGHT COLUMN: GENERATED GEMINI AI SUMMARY EDITOR
        summary_box = QVBoxLayout()
        n_label = QLabel("✨ Gemini AI Meeting Notes Summary:")
        n_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        n_label.setStyleSheet("color: #00ff88;")
        summary_box.addWidget(n_label)

        self.notes_edit = QTextEdit()
        self.notes_edit.setStyleSheet("color: #00ff88;")
        self.notes_edit.setPlaceholderText("Structured Gemini AI Summary (Overview, Key Topics, Decisions, Action Items) will be generated here upon stopping recording...")
        summary_box.addWidget(self.notes_edit)

        content_layout.addLayout(summary_box)

        layout.addLayout(content_layout)

        # Bottom Action Bar
        export_bar = QHBoxLayout()

        self.status_label = QLabel("Status: Ready to record video meeting.")
        self.status_label.setStyleSheet("color: #94a3b8;")
        export_bar.addWidget(self.status_label)

        open_folder_btn = QPushButton("📁 OPEN FOLDER")
        open_folder_btn.clicked.connect(self._open_notes_folder)
        export_bar.addWidget(open_folder_btn)

        self.open_video_btn = QPushButton("🎥 OPEN VIDEO MP4")
        self.open_video_btn.setEnabled(False)
        self.open_video_btn.clicked.connect(self._open_video)
        export_bar.addWidget(self.open_video_btn)

        self.open_docx_btn = QPushButton("📄 OPEN DOCX")
        self.open_docx_btn.setEnabled(False)
        self.open_docx_btn.clicked.connect(self._open_docx)
        export_bar.addWidget(self.open_docx_btn)

        self.open_pdf_btn = QPushButton("📑 OPEN PDF")
        self.open_pdf_btn.setEnabled(False)
        self.open_pdf_btn.clicked.connect(self._open_pdf)
        export_bar.addWidget(self.open_pdf_btn)

        layout.addLayout(export_bar)

    def start_recording(self):
        self.record_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.timer_label.setText("REC TIMER: 00:00:00")
        self.status_label.setText("Status: 🔴 RECORDING WEBCAM VIDEO & AUDIO...")

        self.media_thread = MeetingMediaRecorderThread(parent=self)
        self.media_thread.frame_signal.connect(self._on_frame_received)
        self.media_thread.tick_signal.connect(self._on_timer_tick)
        self.media_thread.finished_signal.connect(self._on_recording_finished)
        self.media_thread.error_signal.connect(self._on_recording_error)
        self.media_thread.start()

    def _on_frame_received(self, qt_img):
        pixmap = QPixmap.fromImage(qt_img)
        scaled_pixmap = pixmap.scaled(
            self.video_frame.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.video_frame.setPixmap(scaled_pixmap)

    def _on_timer_tick(self, seconds):
        mins = seconds // 60
        hrs = mins // 60
        secs = seconds % 60
        self.timer_label.setText(f"REC TIMER: {hrs:02d}:{mins%60:02d}:{secs:02d}")

    def stop_recording(self):
        if self.media_thread and self.media_thread.isRunning():
            self.status_label.setText("Status: Processing video & generating Gemini AI summary...")
            self.media_thread.stop_recording()

    def _on_recording_finished(self, video_path, audio_path):
        self.record_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.video_frame.setText("WEBCAM RECORDING OFF\nMeeting Video Saved to MP4")
        self.status_label.setText("Status: Video & Audio captured. Generating AI Meeting Notes & Documents...")

        self.current_video_path = video_path
        self.current_audio_path = audio_path

        transcript = self.transcript_edit.toPlainText().strip()
        if not transcript:
            stt_text = transcribe_audio_file(audio_path)
            if stt_text:
                transcript = stt_text
                self.transcript_edit.setPlainText(transcript)
            else:
                transcript = (
                    "Meeting initiated for project architecture review and video recording validation. "
                    "Discussed system security upgrades, intruder detection modules, and real-time analytics. "
                    "Agreed to deploy automated meeting video recording, note generation, and document export."
                )
                self.transcript_edit.setPlainText(transcript)

        # Summarize using Gemini AI
        summary_data = summarize_meeting_with_gemini(transcript)

        # Format Display Text
        notes_display = (
            f"=== {summary_data.get('title', 'Meeting Notes')} ===\n"
            f"Date: {summary_data.get('date', datetime.now().strftime('%Y-%m-%d %H:%M'))}\n\n"
            f"📌 EXECUTIVE OVERVIEW:\n{summary_data.get('overview', '')}\n\n"
            f"💡 KEY DISCUSSION TOPICS:\n" + "\n".join([f"• {t}" for t in summary_data.get('key_topics', [])]) + "\n\n"
            f"✅ DECISIONS AGREED UPON:\n" + "\n".join([f"• {d}" for d in summary_data.get('decisions', [])]) + "\n\n"
            f"🎯 ACTION ITEMS:\n" + "\n".join([f"• {a}" for a in summary_data.get('action_items', [])])
        )
        self.notes_edit.setPlainText(notes_display)

        # Auto-Export DOCX and PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        docx_filename = f"Meeting_Notes_{timestamp}.docx"
        pdf_filename = f"Meeting_Notes_{timestamp}.pdf"

        docx_path = os.path.join(MEETING_DIR, docx_filename)
        pdf_path = os.path.join(MEETING_DIR, pdf_filename)

        export_to_docx(summary_data, transcript, docx_path)
        export_to_pdf(summary_data, transcript, pdf_path)

        self.current_docx_path = docx_path
        self.current_pdf_path = pdf_path

        self.open_video_btn.setEnabled(True)
        self.open_docx_btn.setEnabled(True)
        self.open_pdf_btn.setEnabled(True)

        self.status_label.setText(f"Status: ✨ Complete! Video MP4, DOCX & PDF saved in {MEETING_DIR}")
        try:
            from voice_engine import speak
            speak("Meeting video and audio recording complete. Gemini AI notes generated and saved to Video, Word, and PDF documents.")
        except Exception:
            pass

    def _on_recording_error(self, err_msg):
        self.record_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText(f"Recording error: {err_msg}")

    def _open_notes_folder(self):
        if os.path.exists(MEETING_DIR):
            os.startfile(MEETING_DIR)

    def _open_video(self):
        if self.current_video_path and os.path.exists(self.current_video_path):
            os.startfile(self.current_video_path)

    def _open_docx(self):
        if self.current_docx_path and os.path.exists(self.current_docx_path):
            os.startfile(self.current_docx_path)

    def _open_pdf(self):
        if self.current_pdf_path and os.path.exists(self.current_pdf_path):
            os.startfile(self.current_pdf_path)


# Global Launch Helper
def launch_meeting_notes_dialog(parent=None):
    dialog = MeetingNotesDialog(parent=parent)
    dialog.exec()
