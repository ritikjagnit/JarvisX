import os
import sys
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

def generate_pdf():
    pdf_filename = "JarvisX_AtoZ_Feature_Guide_2026.pdf"
    
    # Page setup - 0.5 inch margins for content density
    doc = SimpleDocTemplate(
        pdf_filename, 
        pagesize=letter, 
        rightMargin=36, 
        leftMargin=36, 
        topMargin=36, 
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle', 
        parent=styles['Heading1'], 
        fontName='Helvetica-Bold', 
        fontSize=22, 
        textColor=colors.HexColor("#0f172a"), 
        spaceAfter=4,
        alignment=1 # Centered
    )
    
    sub_style = ParagraphStyle(
        'DocSub', 
        parent=styles['Normal'], 
        fontName='Helvetica-Bold', 
        fontSize=11, 
        textColor=colors.HexColor("#0284c7"), 
        spaceAfter=15,
        alignment=1 # Centered
    )
    
    section_title = ParagraphStyle(
        'SecTitle', 
        parent=styles['Heading2'], 
        fontName='Helvetica-Bold', 
        fontSize=13, 
        textColor=colors.HexColor("#0f172a"), 
        spaceBefore=12, 
        spaceAfter=6
    )
    
    body_text = ParagraphStyle(
        'BodyTextCustom', 
        parent=styles['Normal'], 
        fontName='Helvetica', 
        fontSize=9.5, 
        leading=13.5, 
        textColor=colors.HexColor("#334155"), 
        spaceAfter=8
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader', 
        parent=styles['Normal'], 
        fontName='Helvetica-Bold', 
        fontSize=9.5, 
        textColor=colors.white
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell', 
        parent=styles['Normal'], 
        fontName='Helvetica', 
        fontSize=9, 
        leading=12,
        textColor=colors.HexColor("#1e293b")
    )
    
    table_cell_bold = ParagraphStyle(
        'TableCellBold', 
        parent=styles['Normal'], 
        fontName='Helvetica-Bold', 
        fontSize=9, 
        leading=12,
        textColor=colors.HexColor("#0f172a")
    )

    story = []
    
    # Header Title
    story.append(Paragraph("J.A.R.V.I.S. X — SYSTEM FEATURE MATRIX & INTERFACE GUIDE", title_style))
    story.append(Paragraph(f"Ultimate local AI Assistant Platform  |  Compiled: {datetime.now().strftime('%d %B %Y')}", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#0284c7"), spaceAfter=15))
    
    # Introduction
    intro_p = (
        "Welcome to the official <b>J.A.R.V.I.S. X</b> feature matrix guide. This document details the "
        "complete list of modular subsystems, biometric gates, artificial intelligence evaluators, and security "
        "vaults currently integrated into your assistant, along with the precise voice and text commands used to trigger them."
    )
    story.append(Paragraph(intro_p, body_text))
    story.append(Spacer(1, 10))
    
    # Feature Matrix Table Header
    story.append(Paragraph("Core Feature Command & Activation Matrix", section_title))
    
    # Table Data Definition
    data = [
        [
            Paragraph("Module / Feature Name", table_header_style),
            Paragraph("Trigger Commands (Voice & Text)", table_header_style),
            Paragraph("Core Functionality & Exporter Output", table_header_style)
        ]
    ]
    
    matrix_rows = [
        (
            "👤 Biometric Security Gateway",
            "Automatic Launch at Boot / 'register biometrics'",
            "Three-way startup auth selection gateway (Face Login, Voice Login, Biometrics Registration) with hardware isolation protocol."
        ),
        (
            "🎥 Automated Meeting Notes",
            "'record meeting', 'start meeting', 'meeting notes', 'summarize meeting'",
            "Simultaneous OpenCV webcam video and 16kHz microphone audio recording. Merges audio inside MP4 using FFMpeg. STT transcript transcription + Gemini Executive Summary. Exporter: DOCX + PDF meeting notes."
        ),
        (
            "📊 AI Resume Analyzer",
            "'analyze resume', 'resume analyzer', 'check my resume', 'resume score'",
            "Parses PDF, DOCX, and TXT resumes. Evaluates candidate against target role for ATS score (0-100%), strengths, weaknesses, and step-by-step career path ('Tu ye ye kar'). Exporter: DOCX + PDF evaluation scorecard."
        ),
        (
            "🌐 Web Research & News",
            "'tech news', 'latest news', 'news digest', 'web research'",
            "Live RSS aggregator (Tech & AI, Markets, Cybersecurity, Global). Gemini AI synthesizes custom summaries. Neural voice speak output. Exporter: DOCX + PDF news reports."
        ),
        (
            "🔒 Encrypted Password Manager",
            "'cyber vault', 'password manager', 'open vault', 'passwords'",
            "AES-256 encrypted storage of logins, passwords, and API keys. Biometric face/voice gateway lock. Random password generator with entropy meter. 15-second clipboard auto-wipe. 60-second auto-lock."
        ),
        (
            "🎙️ AI Interview Coach",
            "'mock interview', 'interview coach', 'practice interview', 'mock test'",
            "Technical/behavioral mock interview & MCQ Quiz mode with 4 interactive cyberpunk buttons. Instant accuracy feedback, AI explanation, live score gauge, and scorecard generation. Exporter: DOCX + PDF."
        ),
        (
            "📁 Duplicate File Detector",
            "'duplicate file', 'scan duplicates', 'find duplicates', 'duplicate finder'",
            "Dual-pass SHA-256 scanner that scans files, compares checksum hashes, and prompts user to clean duplicates cleanly."
        ),
        (
            "🛡️ Background Intruder Detector",
            "'start intruder detector', 'stop intruder detector', 'intruder'",
            "Continuous background webcam feed security monitoring using local OpenCV motion detection to log unauthorized physical access attempts."
        )
    ]
    
    for row in matrix_rows:
        data.append([
            Paragraph(row[0], table_cell_bold),
            Paragraph(row[1], table_cell_style),
            Paragraph(row[2], table_cell_style)
        ])
        
    t = Table(data, colWidths=[120, 180, 240])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    
    story.append(t)
    
    # Document Build
    doc.build(story)
    print(f"[GUIDE GENERATOR] PDF saved successfully: {pdf_filename}")

if __name__ == "__main__":
    generate_pdf()
