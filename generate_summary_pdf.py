import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether

def build_pdf():
    pdf_filename = "JarvisX_Implementation_Summary_2026.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY_COLOR = colors.HexColor("#020617")   # Dark Space Navy
    ACCENT_CYAN = colors.HexColor("#0088cc")     # Cyan Accent
    ACCENT_GREEN = colors.HexColor("#008855")    # Emerald Accent
    TEXT_DARK = colors.HexColor("#1e293b")       # Slate
    BG_LIGHT = colors.HexColor("#f8fafc")        # Light Gray

    # Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY_COLOR,
        alignment=0, # Left-aligned
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

    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=PRIMARY_COLOR,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=TEXT_DARK,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    story = []

    # Title & Header
    story.append(Paragraph("INTELLIGENT AI SYSTEM IMPLEMENTATION REPORT", title_style))
    story.append(Paragraph("Developer: Shravani  |  Date: July 22, 2026  |  Project: Intelligent AI Ecosystem", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT_CYAN, spaceAfter=12))

    # Executive Summary Paragraph
    exec_summary = (
        "<b>Executive Summary:</b> Today's session focused on upgrading JarvisX with enterprise-grade biometric security, "
        "background intruder detection, voice-controlled browser and screen interactions, an interactive Streamlit system "
        "analytics dashboard, duplicate file scanning with SHA256 cryptographic verification, and a unified lazy-loading "
        "biometric authentication gateway."
    )
    story.append(Paragraph(exec_summary, body_style))
    story.append(Spacer(1, 8))

    # Table of Implemented Features
    table_data = [
        [Paragraph("<b>#</b>", body_style), Paragraph("<b>Feature Module</b>", body_style), Paragraph("<b>Core Technologies / Files</b>", body_style), Paragraph("<b>Status</b>", body_style)],
        [Paragraph("1", body_style), Paragraph("Biometric Voice Authentication", body_style), Paragraph("MFCC + Delta, L2 Cosine Matching, SciPy<br/><i>voice_auth.py</i>", body_style), Paragraph("<font color='#008855'><b>COMPLETED</b></font>", body_style)],
        [Paragraph("2", body_style), Paragraph("Intruder Detection System", body_style), Paragraph("OpenCV, face_recognition, JSON Audit<br/><i>intruder_detector.py</i>", body_style), Paragraph("<font color='#008855'><b>COMPLETED</b></font>", body_style)],
        [Paragraph("3", body_style), Paragraph("Screen Scroll & Media Controls", body_style), Paragraph("PyAutoGUI, Browser Automation<br/><i>browser_control.py</i>", body_style), Paragraph("<font color='#008855'><b>COMPLETED</b></font>", body_style)],
        [Paragraph("4", body_style), Paragraph("Streamlit Analytics Dashboard", body_style), Paragraph("Streamlit, Plotly, Pandas, Psutil<br/><i>analytics_dashboard.py</i>", body_style), Paragraph("<font color='#008855'><b>COMPLETED</b></font>", body_style)],
        [Paragraph("5", body_style), Paragraph("Duplicate File Detector", body_style), Paragraph("SHA256 Chunk Hashing, PyQt6 Tree View<br/><i>duplicate_finder.py</i>", body_style), Paragraph("<font color='#008855'><b>COMPLETED</b></font>", body_style)],
        [Paragraph("6", body_style), Paragraph("Biometric Auth Selection Gateway", body_style), Paragraph("Lazy Hardware Loading, PyQt6 Gateway<br/><i>auth_portal.py</i>", body_style), Paragraph("<font color='#008855'><b>COMPLETED</b></font>", body_style)],
        [Paragraph("7", body_style), Paragraph("Neural Voice & System Resiliency", body_style), Paragraph("edge-tts (Prabhat/Neerja), OpenCV Guard<br/><i>voice_engine.py, main.py</i>", body_style), Paragraph("<font color='#008855'><b>COMPLETED</b></font>", body_style)],
    ]

    t = Table(table_data, colWidths=[25, 150, 240, 95])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

    # Section 1: Biometric Voice & Intruder Detection
    story.append(Paragraph("1. Biometric Security & Intruder Protection Engine", heading_style))
    story.append(Paragraph("• <b>Voice Biometrics (voice_auth.py):</b> Extracted 54-dimensional MFCC, Delta MFCC, and Spectral Centroid features with energy VAD. Implemented cosine similarity speaker verification (threshold 68%). Integrated pre-command security guard.", bullet_style))
    story.append(Paragraph("• <b>Intruder Defense (intruder_detector.py):</b> Created background webcam scanner (IntruderMonitorThread) that detects unknown faces, captures photo evidence with red HUD overlay to <i>jarvis_data/intruders/</i>, and logs records to <i>intruder_log.json</i>.", bullet_style))
    story.append(Paragraph("• <b>Biometric Gateway Portal (auth_portal.py):</b> Built startup authentication selection screen offering Face Login vs Voice Login choice. Ensured webcam hardware stays OFF until Face Login is selected.", bullet_style))

    # Section 2: Screen Controls & Streamlit Analytics
    story.append(Paragraph("2. Screen Control & Streamlit Analytics Dashboard", heading_style))
    story.append(Paragraph("• <b>Screen Scroll & YouTube Controls (browser_control.py):</b> Implemented voice/text commands for screen scroll down/up/top/bottom, YouTube video play/pause (k), mute (m), fullscreen (f), theater mode (t), skip/rewind, volume adjustment, and browser tab controls.", bullet_style))
    story.append(Paragraph("• <b>Streamlit Analytics App (analytics_dashboard.py & analytics_logger.py):</b> Real-time command telemetry logger and interactive Streamlit web app displaying Total Commands, Daily Usage area chart, Weekly Usage bar chart, Top 10 Leaderboard, Hardware Performance gauges (CPU, RAM, Disk, Threads), and Voice Accuracy audit.", bullet_style))

    # Section 3: Duplicate File Detector & System Stability
    story.append(Paragraph("3. Duplicate File Detector & Project Resiliency", heading_style))
    story.append(Paragraph("• <b>Duplicate Detector (duplicate_finder.py):</b> Independent high-performance 2-pass duplicate scanner grouping files by size first and calculating SHA256 hashes for size matches. Features interactive PyQt6 tree widget with double-confirmation file deletion.", bullet_style))
    story.append(Paragraph("• <b>Neural Voice Synthesis (voice_engine.py & edge-tts):</b> Installed <i>edge-tts</i> for natural Indian English Neural Voice output (en-IN-PrabhatNeural / en-IN-NeerjaNeural).", bullet_style))
    story.append(Paragraph("• <b>OpenCV & Math Safeguards:</b> Wrapped OpenCV camera capture calls in try-except blocks to eliminate C++ driver crashes and added NaN/Inf float safeguards across audio visualization widgets.", bullet_style))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
    story.append(Paragraph("<b>Verification Result:</b> All modules audited, unit tested, and verified 100% operational.", ParagraphStyle('Footer', parent=body_style, fontSize=8, textColor=colors.HexColor("#64748b"))))

    doc.build(story)
    print(f"SUCCESS: PDF report generated at {os.path.abspath(pdf_filename)}")

if __name__ == "__main__":
    build_pdf()
