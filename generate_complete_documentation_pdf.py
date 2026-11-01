import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak, KeepTogether

def build_complete_pdf():
    pdf_filename = "JarvisX_Complete_Architecture_Flowcharts_2026.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Color Palette
    PRIMARY_COLOR = colors.HexColor("#020617")   # Dark Space Navy
    ACCENT_CYAN = colors.HexColor("#0088cc")     # Cyan Accent
    ACCENT_GREEN = colors.HexColor("#008855")    # Emerald Accent
    ACCENT_PURPLE = colors.HexColor("#7c3aed")   # Purple Accent
    TEXT_DARK = colors.HexColor("#1e293b")       # Slate
    BG_LIGHT = colors.HexColor("#f8fafc")        # Light Gray
    CODE_BG = colors.HexColor("#0f172a")         # Dark Code Box

    # Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=PRIMARY_COLOR,
        alignment=0,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=ACCENT_CYAN,
        spaceAfter=15
    )

    heading1_style = ParagraphStyle(
        'SectionHeading1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=PRIMARY_COLOR,
        spaceBefore=14,
        spaceAfter=6
    )

    heading2_style = ParagraphStyle(
        'SectionHeading2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=ACCENT_CYAN,
        spaceBefore=8,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK,
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=TEXT_DARK,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    code_block_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#38bdf8"),
        spaceBefore=4,
        spaceAfter=6
    )

    story = []

    # ---------------- PAGE 1: TITLE & EXECUTIVE OVERVIEW ----------------
    story.append(Paragraph("INTELLIGENT AI SYSTEM ARCHITECTURE & FEATURE MANUAL", title_style))
    story.append(Paragraph("Complete Technical Documentation, Workflow Flowcharts & Module Reference | Author: Shravani", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT_CYAN, spaceAfter=12))

    overview_text = (
        "<b>Project Overview:</b> Intelligent AI is a next-generation AI assistant featuring multi-modal biometric security "
        "(Face Recognition & MFCC Voice Authentication), non-intrusive background intruder detection, voice-controlled screen scrolling "
        "and media playback, an interactive Streamlit system telemetry dashboard, SHA256 duplicate file detector, and a "
        "lazy-loading biometric authentication gateway. This document provides complete end-to-end technical details, "
        "system flowcharts, and operational guides for every feature."
    )
    story.append(Paragraph(overview_text, body_style))
    story.append(Spacer(1, 8))

    # SYSTEM ARCHITECTURE FLOWCHART DIAGRAM (ASCII / GRAPHICAL TABLE)
    story.append(Paragraph("System Architecture & Data Flowchart", heading1_style))

    flowchart_box = [
        [Paragraph("<b>[ SYSTEM BOOT (main.py) ]</b><br/>Bootstrap Local Packages & DPI Awareness", body_style)],
        [Paragraph("↓", body_style)],
        [Paragraph("<b>[ BIOMETRIC AUTH GATEWAY (auth_portal.py) ]</b><br/>Hardware Lazy-Loading Selection Screen (Webcam OFF)", body_style)],
        [Paragraph("↙ &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; ↘", body_style)],
        [Paragraph("<b>👤 FACE RECOGNITION (face_auth.py)</b><br/>OpenCV + 128-d HOG Encodings", body_style), Paragraph("<b>🎤 VOICE BIOMETRICS (voice_auth.py)</b><br/>54-d MFCC + Cosine Similarity (68%)", body_style)],
        [Paragraph("↘ &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; ↙", body_style)],
        [Paragraph("<b>[ JARVIS MAIN DASHBOARD & THREAD WORKER QUEUE ]</b><br/>Matrix Digital Rain + Arc Reactor Core UI + CommandWorker", body_style)],
        [Paragraph("↓ &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; ↓ &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; ↓ &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; ↓", body_style)],
        [
            Paragraph("<b>🛡️ DEFENSE</b><br/>Intruder Monitor", body_style),
            Paragraph("<b>📜 SCREEN CTRL</b><br/>Scroll & YouTube", body_style),
            Paragraph("<b>📊 ANALYTICS</b><br/>Streamlit App", body_style),
            Paragraph("<b>🔍 DUPLICATES</b><br/>SHA256 Detector", body_style)
        ]
    ]

    fc_table = Table(flowchart_box, colWidths=[130, 130, 130, 130])
    fc_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#e2e8f0")),
        ('BACKGROUND', (0,2), (-1,2), colors.HexColor("#f1f5f9")),
        ('BACKGROUND', (0,6), (-1,6), colors.HexColor("#e2e8f0")),
        ('BACKGROUND', (0,8), (-1,8), colors.HexColor("#f8fafc")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(fc_table)
    story.append(Spacer(1, 10))

    # ---------------- PAGE 2: IN-DEPTH MODULE DOCUMENTATION ----------------
    story.append(Paragraph("1. System Boot & Biometric Security Gateway", heading1_style))
    story.append(Paragraph("• <b>App Startup (main.py):</b> Bootstraps virtual environment site-packages automatically. Configures Windows per-monitor DPI awareness. Starts global Arc Reactor animations.", bullet_style))
    story.append(Paragraph("• <b>Biometric Gateway Portal (auth_portal.py):</b> Opens futuristic security selection screen. Keeps webcam hardware 100% OFF until Face Login is selected. Displays live counts of enrolled Face Prints & Voice Profiles.", bullet_style))
    story.append(Paragraph("• <b>Window Isolation Protocol:</b> When Face or Voice login is chosen, the portal hides cleanly (self.hide()) so the authentication dialog renders in standalone full view without overlapping UI artifacts.", bullet_style))

    story.append(Paragraph("2. Biometric Authentication & Intruder Detection Engines", heading1_style))
    story.append(Paragraph("• <b>Face Authentication Engine (face_auth.py):</b> Uses OpenCV (cv2.VideoCapture(0)) and dlib/face_recognition HOG model to extract 128-dimensional facial encodings. Compares encodings against <i>jarvis_data/face_auth.json</i> with Euclidean distance thresholding. Features cyan holographic scanner HUD.", bullet_style))
    story.append(Paragraph("• <b>Voice Biometrics Engine (voice_auth.py):</b> Extracts 54-dimensional feature vectors (MFCC, Delta MFCCs, Spectral Centroid) with Energy-based Voice Activity Detection (VAD). Performs L2-normalized cosine similarity matching against <i>jarvis_data/voice_auth.json</i> (68% similarity threshold). Includes AudioSpectrumWidget waveform visualizer.", bullet_style))
    story.append(Paragraph("• <b>Intruder Detection System (intruder_detector.py):</b> Background worker (IntruderMonitorThread) scans webcam every 3 seconds post-login. Detects unknown faces for 2+ consecutive checks, captures photo evidence with red HUD overlay to <i>jarvis_data/intruders/</i>, logs incident to <i>intruder_log.json</i>, and pops up IntruderAlertDialog.", bullet_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("3. Screen Control, YouTube Automation & Analytics", heading1_style))
    story.append(Paragraph("• <b>Screen Scroll & Browser Navigation (browser_control.py):</b> Uses PyAutoGUI to execute voice/text screen scrolling (down, up, top, bottom) and full YouTube media playback controls: Play/Pause (k), Mute (m), Fullscreen (f), Theater mode (t), Skip (l), Rewind (j), Next Video (Shift+N), Volume Up/Down, and Tab Controls (Close Tab, New Tab, Refresh).", bullet_style))
    story.append(Paragraph("• <b>Streamlit Analytics Dashboard (analytics_dashboard.py & analytics_logger.py):</b> Real-time command telemetry engine logging timestamp, date, day of week, source, category, and voice confidence score to <i>jarvis_data/analytics.json</i>. Features Streamlit web app displaying Total Commands, Daily Usage area chart, Weekly Usage bar chart, Top 10 Leaderboard, Category breakdown donut chart, System Hardware diagnostics (CPU, RAM, Disk, Threads via psutil), and Voice Accuracy audit.", bullet_style))

    story.append(Paragraph("4. Duplicate File Detector & Project Resiliency", heading1_style))
    story.append(Paragraph("• <b>Duplicate File Detector (duplicate_finder.py):</b> Independent high-performance 2-pass scanner: Pass 1 groups files by size; Pass 2 calculates SHA256 cryptographic hashes (64KB chunks) for matching sizes. Features PyQt6 tree widget with double-confirmation file deletion and freed disk space reporting.", bullet_style))
    story.append(Paragraph("• <b>Neural Voice Synthesis (voice_engine.py & edge-tts):</b> Uses <i>edge-tts</i> for natural Indian English Neural Voice output (en-IN-PrabhatNeural / en-IN-NeerjaNeural) with automatic SAPI5 offline fallback.", bullet_style))
    story.append(Paragraph("• <b>OpenCV & Math Safeguards:</b> Wrapped OpenCV frame reads in try-except blocks to eliminate C++ driver crashes and added NaN/Inf float safeguards across audio visualization widgets.", bullet_style))

    story.append(Spacer(1, 10))

    # Comprehensive Feature Function Matrix Table
    story.append(Paragraph("Complete Feature Command & Workflow Reference Table", heading1_style))

    ref_data = [
        [Paragraph("<b>Feature Category</b>", body_style), Paragraph("<b>Trigger Command / Action</b>", body_style), Paragraph("<b>Target Module</b>", body_style), Paragraph("<b>Output Action</b>", body_style)],
        [Paragraph("Biometric Gateway", body_style), Paragraph("App Launch / Boot", body_style), Paragraph("auth_portal.py", body_style), Paragraph("Opens Security Gateway (Webcam OFF)", body_style)],
        [Paragraph("Face Auth", body_style), Paragraph("Click 'ACCESS WITH FACE'", body_style), Paragraph("face_auth.py", body_style), Paragraph("Opens Camera, verifies face encoding", body_style)],
        [Paragraph("Voice Auth", body_style), Paragraph("Click 'ACCESS WITH VOICE'", body_style), Paragraph("voice_auth.py", body_style), Paragraph("Captures audio, verifies MFCC cosine similarity", body_style)],
        [Paragraph("Intruder Defense", body_style), Paragraph("'start intruder detection'", body_style), Paragraph("intruder_detector.py", body_style), Paragraph("Background webcam scan, saves photo evidence", body_style)],
        [Paragraph("Screen Control", body_style), Paragraph("'scroll down' / 'scroll up'", body_style), Paragraph("browser_control.py", body_style), Paragraph("PyAutoGUI smooth page scroll", body_style)],
        [Paragraph("YouTube Control", body_style), Paragraph("'pause' / 'fullscreen' / 'skip'", body_style), Paragraph("browser_control.py", body_style), Paragraph("Executes native browser media shortcuts", body_style)],
        [Paragraph("Analytics App", body_style), Paragraph("'open analytics' / Button", body_style), Paragraph("analytics_dashboard.py", body_style), Paragraph("Launches Streamlit Web App (port 8501)", body_style)],
        [Paragraph("Duplicate Finder", body_style), Paragraph("'scan duplicates' / 'find duplicates'", body_style), Paragraph("duplicate_finder.py", body_style), Paragraph("SHA256 2-pass scan & deletion UI", body_style)],
        [Paragraph("Neural Voice", body_style), Paragraph("Any Speech Output", body_style), Paragraph("voice_engine.py", body_style), Paragraph("Generates edge-tts Prabhat/Neerja voice", body_style)],
    ]

    t_ref = Table(ref_data, colWidths=[100, 150, 120, 150])
    t_ref.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#00ffff")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_ref)

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
    story.append(Paragraph("<b>JarvisX End-to-End System Manual</b> • Complete System Verification 100% Operational", ParagraphStyle('Footer', parent=body_style, fontSize=8, textColor=colors.HexColor("#64748b"))))

    doc.build(story)
    print(f"SUCCESS: Complete system documentation PDF generated at {os.path.abspath(pdf_filename)}")

if __name__ == "__main__":
    build_complete_pdf()
