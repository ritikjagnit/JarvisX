"""
Vector Icon Factory for JarvisX AI OS
Generates high-definition, anti-aliased, professional vector icons using PyQt6 QPainter & QPainterPath.
Eliminates generic emojis in favor of sleek, human-designed enterprise iconography.
"""

from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath, QIcon
from PyQt6.QtCore import Qt, QPointF, QRectF

def _create_base_pixmap(size=64):
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    return pix

def draw_dashboard_icon(size=64, color_hex="#3B82F6"):
    pix = _create_base_pixmap(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    col = QColor(color_hex)
    painter.setPen(QPen(col, 2.5))
    painter.setBrush(QBrush(QColor(col.red(), col.green(), col.blue(), 40)))

    # Outer rounded square grid
    w = size
    pad = int(w * 0.15)
    box_s = int(w * 0.28)
    gap = int(w * 0.14)

    # 4 Tech Quadrants
    for r in range(2):
        for c in range(2):
            x = pad + c * (box_s + gap)
            y = pad + r * (box_s + gap)
            painter.drawRoundedRect(QRectF(x, y, box_s, box_s), 4, 4)

    # Central Core Accent Dot
    painter.setBrush(QBrush(QColor("#60A5FA")))
    painter.drawEllipse(QPointF(w/2, w/2), 3, 3)

    painter.end()
    return QIcon(pix)

def draw_voice_icon(size=64, color_hex="#10B981"):
    pix = _create_base_pixmap(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    col = QColor(color_hex)
    painter.setPen(QPen(col, 2.5))
    painter.setBrush(QBrush(QColor(col.red(), col.green(), col.blue(), 30)))

    # Microphone Capsule
    w = size
    mic_w = int(w * 0.26)
    mic_h = int(w * 0.42)
    mic_x = int((w - mic_w) / 2)
    mic_y = int(w * 0.15)
    
    painter.drawRoundedRect(QRectF(mic_x, mic_y, mic_w, mic_h), mic_w/2, mic_w/2)

    # Mic Stand Arc
    arc_rect = QRectF(w*0.22, w*0.3, w*0.56, w*0.42)
    painter.drawArc(arc_rect, 190 * 16, 160 * 16)

    # Base Line
    painter.drawLine(int(w*0.5), int(w*0.72), int(w*0.5), int(w*0.84))
    painter.drawLine(int(w*0.36), int(w*0.84), int(w*0.64), int(w*0.84))

    painter.end()
    return QIcon(pix)

def draw_chat_icon(size=64, color_hex="#8B5CF6"):
    pix = _create_base_pixmap(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    col = QColor(color_hex)
    painter.setPen(QPen(col, 2.2))
    painter.setBrush(QBrush(QColor(col.red(), col.green(), col.blue(), 40)))

    # Main Chat Bubble
    w = size
    path1 = QPainterPath()
    path1.addRoundedRect(QRectF(w*0.14, w*0.16, w*0.58, w*0.44), 10, 10)
    painter.drawPath(path1)

    # Overlapping Accent Bubble
    painter.setPen(QPen(QColor("#60A5FA"), 2))
    painter.setBrush(QBrush(QColor(96, 165, 250, 60)))
    path2 = QPainterPath()
    path2.addRoundedRect(QRectF(w*0.32, w*0.38, w*0.54, w*0.42), 8, 8)
    painter.drawPath(path2)

    # Prompt Lines inside chat
    painter.setPen(QPen(QColor("#E2E8F0"), 2))
    painter.drawLine(int(w*0.42), int(w*0.52), int(w*0.72), int(w*0.52))
    painter.drawLine(int(w*0.42), int(w*0.62), int(w*0.64), int(w*0.62))

    painter.end()
    return QIcon(pix)

def draw_vision_icon(size=64, color_hex="#10B981"):
    pix = _create_base_pixmap(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    col = QColor(color_hex)
    w = size

    # Optical Iris Ring
    painter.setPen(QPen(col, 2.5))
    painter.setBrush(QBrush(QColor(col.red(), col.green(), col.blue(), 30)))

    eye_path = QPainterPath()
    eye_path.moveTo(w*0.12, w*0.5)
    eye_path.quadTo(w*0.5, w*0.14, w*0.88, w*0.5)
    eye_path.quadTo(w*0.5, w*0.86, w*0.12, w*0.5)
    painter.drawPath(eye_path)

    # Pupil Core & Reticle Crosshair
    painter.drawEllipse(QPointF(w*0.5, w*0.5), w*0.16, w*0.16)
    painter.setBrush(QBrush(QColor("#3B82F6")))
    painter.drawEllipse(QPointF(w*0.5, w*0.5), w*0.06, w*0.06)

    # Corner Reticle Markers
    painter.setPen(QPen(QColor("#60A5FA"), 1.8))
    d = w * 0.12
    # Top Left
    painter.drawLine(int(w*0.18), int(w*0.25), int(w*0.18 + d), int(w*0.25))
    painter.drawLine(int(w*0.18), int(w*0.25), int(w*0.18), int(w*0.25 + d))
    # Bottom Right
    painter.drawLine(int(w*0.82), int(w*0.75), int(w*0.82 - d), int(w*0.75))
    painter.drawLine(int(w*0.82), int(w*0.75), int(w*0.82), int(w*0.75 - d))

    painter.end()
    return QIcon(pix)

def draw_doc_icon(size=64, color_hex="#F59E0B"):
    pix = _create_base_pixmap(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    col = QColor(color_hex)
    w = size

    # Document Sheet with Folded Corner
    painter.setPen(QPen(col, 2.4))
    painter.setBrush(QBrush(QColor(col.red(), col.green(), col.blue(), 30)))

    doc_path = QPainterPath()
    doc_path.moveTo(w*0.24, w*0.14)
    doc_path.lineTo(w*0.58, w*0.14)
    doc_path.lineTo(w*0.76, w*0.32)
    doc_path.lineTo(w*0.76, w*0.86)
    doc_path.lineTo(w*0.24, w*0.86)
    doc_path.closeSubpath()
    painter.drawPath(doc_path)

    # Fold Line
    painter.drawLine(int(w*0.58), int(w*0.14), int(w*0.58), int(w*0.32))
    painter.drawLine(int(w*0.58), int(w*0.32), int(w*0.76), int(w*0.32))

    # Text Lines inside Document
    painter.setPen(QPen(QColor("#60A5FA"), 2))
    painter.drawLine(int(w*0.34), int(w*0.44), int(w*0.66), int(w*0.44))
    painter.drawLine(int(w*0.34), int(w*0.56), int(w*0.66), int(w*0.56))
    painter.drawLine(int(w*0.34), int(w*0.68), int(w*0.54), int(w*0.68))

    painter.end()
    return QIcon(pix)

def draw_security_icon(size=64, color_hex="#EF4444"):
    pix = _create_base_pixmap(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    col = QColor(color_hex)
    w = size

    # Hexagonal Armor Shield
    painter.setPen(QPen(col, 2.5))
    painter.setBrush(QBrush(QColor(col.red(), col.green(), col.blue(), 40)))

    shield_path = QPainterPath()
    shield_path.moveTo(w*0.5, w*0.12)
    shield_path.lineTo(w*0.84, w*0.24)
    shield_path.lineTo(w*0.84, w*0.56)
    shield_path.quadTo(w*0.5, w*0.9, w*0.5, w*0.9)
    shield_path.quadTo(w*0.16, w*0.56, w*0.16, w*0.56)
    shield_path.lineTo(w*0.16, w*0.24)
    shield_path.closeSubpath()
    painter.drawPath(shield_path)

    # Keyhole Lock Accent
    painter.setPen(QPen(QColor("#F8FAFC"), 2))
    painter.setBrush(QBrush(QColor("#F8FAFC")))
    painter.drawEllipse(QPointF(w*0.5, w*0.42), w*0.08, w*0.08)
    
    key_path = QPainterPath()
    key_path.moveTo(w*0.46, w*0.46)
    key_path.lineTo(w*0.54, w*0.46)
    key_path.lineTo(w*0.56, w*0.64)
    key_path.lineTo(w*0.44, w*0.64)
    key_path.closeSubpath()
    painter.drawPath(key_path)

    painter.end()
    return QIcon(pix)

def draw_analytics_icon(size=64, color_hex="#06B6D4"):
    pix = _create_base_pixmap(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    col = QColor(color_hex)
    w = size

    # Axis Base Lines
    painter.setPen(QPen(QColor("#475569"), 2))
    painter.drawLine(int(w*0.16), int(w*0.84), int(w*0.84), int(w*0.84))
    painter.drawLine(int(w*0.16), int(w*0.84), int(w*0.16), int(w*0.16))

    # Telemetry Trend Line Curve
    painter.setPen(QPen(col, 2.6))
    trend_path = QPainterPath()
    trend_path.moveTo(w*0.2, w*0.74)
    trend_path.lineTo(w*0.38, w*0.56)
    trend_path.lineTo(w*0.54, w*0.64)
    trend_path.lineTo(w*0.82, w*0.26)
    painter.drawPath(trend_path)

    # Data Node Dots
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor("#A78BFA")))
    for pt in [(w*0.2, w*0.74), (w*0.38, w*0.56), (w*0.54, w*0.64), (w*0.82, w*0.26)]:
        painter.drawEllipse(QPointF(pt[0], pt[1]), 3.5, 3.5)

    painter.end()
    return QIcon(pix)

def draw_settings_icon(size=64, color_hex="#94A3B8"):
    pix = _create_base_pixmap(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    col = QColor(color_hex)
    w = size

    # Precision 8-Tooth Gear Wheel
    painter.setPen(QPen(col, 2.2))
    painter.setBrush(QBrush(QColor(col.red(), col.green(), col.blue(), 30)))

    gear_path = QPainterPath()
    center = QPointF(w*0.5, w*0.5)
    gear_path.addEllipse(center, w*0.32, w*0.32)
    painter.drawPath(gear_path)

    # Inner Ring Axle
    painter.setPen(QPen(QColor("#3B82F6"), 2))
    painter.drawEllipse(center, w*0.14, w*0.14)

    # Gear Teeth Accents
    painter.setPen(QPen(col, 3))
    import math
    for i in range(8):
        angle = math.radians(i * 45)
        x1 = w*0.5 + w*0.32 * math.cos(angle)
        y1 = w*0.5 + w*0.32 * math.sin(angle)
        x2 = w*0.5 + w*0.42 * math.cos(angle)
        y2 = w*0.5 + w*0.42 * math.sin(angle)
        painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    painter.end()
    return QIcon(pix)

def draw_search_pixmap(size=32, color_hex="#94A3B8"):
    pix = _create_base_pixmap(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    w = size
    painter.setPen(QPen(QColor(color_hex), 2))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(QRectF(w*0.18, w*0.18, w*0.44, w*0.44))
    painter.drawLine(int(w*0.52), int(w*0.52), int(w*0.82), int(w*0.82))
    painter.end()
    return pix

def draw_bell_pixmap(size=32, color_hex="#60A5FA"):
    pix = _create_base_pixmap(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    w = size
    col = QColor(color_hex)
    painter.setPen(QPen(col, 2))
    painter.setBrush(QBrush(QColor(col.red(), col.green(), col.blue(), 35)))
    
    path = QPainterPath()
    path.moveTo(w*0.5, w*0.14)
    path.quadTo(w*0.22, w*0.3, w*0.22, w*0.62)
    path.lineTo(w*0.14, w*0.74)
    path.lineTo(w*0.86, w*0.74)
    path.lineTo(w*0.78, w*0.62)
    path.quadTo(w*0.78, w*0.3, w*0.5, w*0.14)
    path.closeSubpath()
    painter.drawPath(path)
    
    painter.setBrush(QBrush(col))
    painter.drawEllipse(QPointF(w*0.5, w*0.84), w*0.08, w*0.08)
    painter.end()
    return pix

def draw_user_pixmap(size=32, color_hex="#3B82F6"):
    pix = _create_base_pixmap(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    w = size
    col = QColor(color_hex)
    painter.setPen(QPen(col, 2))
    painter.setBrush(QBrush(QColor(col.red(), col.green(), col.blue(), 45)))
    
    # Head Orb
    painter.drawEllipse(QPointF(w*0.5, w*0.32), w*0.18, w*0.18)
    
    # Body Arc
    body_path = QPainterPath()
    body_path.moveTo(w*0.2, w*0.86)
    body_path.quadTo(w*0.5, w*0.56, w*0.8, w*0.86)
    painter.drawPath(body_path)
    painter.end()
    return pix

def draw_check_pixmap(size=32, color_hex="#10B981"):
    pix = _create_base_pixmap(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    w = size
    col = QColor(color_hex)
    painter.setPen(QPen(col, 2))
    painter.setBrush(QBrush(QColor(col.red(), col.green(), col.blue(), 40)))
    
    painter.drawRoundedRect(QRectF(w*0.14, w*0.14, w*0.72, w*0.72), 6, 6)
    
    painter.setPen(QPen(QColor("#10B981"), 2.4))
    path = QPainterPath()
    path.moveTo(w*0.3, w*0.5)
    path.lineTo(w*0.44, w*0.66)
    path.lineTo(w*0.72, w*0.34)
    painter.drawPath(path)
    painter.end()
    return pix

def draw_folder_pixmap(size=32, color_hex="#60A5FA"):
    pix = _create_base_pixmap(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    w = size
    col = QColor(color_hex)
    painter.setPen(QPen(col, 2))
    painter.setBrush(QBrush(QColor(col.red(), col.green(), col.blue(), 40)))
    
    path = QPainterPath()
    path.moveTo(w*0.14, w*0.28)
    path.lineTo(w*0.4, w*0.28)
    path.lineTo(w*0.5, w*0.38)
    path.lineTo(w*0.86, w*0.38)
    path.lineTo(w*0.86, w*0.8)
    path.lineTo(w*0.14, w*0.8)
    path.closeSubpath()
    painter.drawPath(path)
    painter.end()
    return pix

def draw_interview_prep_pixmap(size=32, color_hex="#3B82F6"):
    """Realistic HD Blue Vector Icon for Interview Prep / Coach."""
    pix = _create_base_pixmap(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    w = size
    col = QColor(color_hex)
    
    # Background Clipboard Frame (Deep Blue Glow)
    painter.setPen(QPen(QColor("#2563EB"), 2))
    painter.setBrush(QBrush(QColor(37, 99, 235, 45)))
    painter.drawRoundedRect(QRectF(w*0.14, w*0.18, w*0.72, w*0.74), 6, 6)

    # Clipboard Top Clip Badge
    painter.setPen(QPen(QColor("#60A5FA"), 2))
    painter.setBrush(QBrush(QColor("#3B82F6")))
    painter.drawRoundedRect(QRectF(w*0.35, w*0.1, w*0.3, w*0.12), 3, 3)

    # Candidate Head Silhouette (Left)
    painter.setPen(QPen(QColor("#60A5FA"), 1.8))
    painter.setBrush(QBrush(QColor(96, 165, 250, 60)))
    painter.drawEllipse(QPointF(w*0.36, w*0.38), w*0.11, w*0.11)
    
    body_path = QPainterPath()
    body_path.moveTo(w*0.22, w*0.62)
    body_path.quadTo(w*0.36, w*0.48, w*0.5, w*0.62)
    painter.drawPath(body_path)

    # Interview Evaluation Checkmark & Lines (Right)
    painter.setPen(QPen(QColor("#38BDF8"), 2))
    painter.drawLine(int(w*0.56), int(w*0.36), int(w*0.78), int(w*0.36))
    painter.drawLine(int(w*0.56), int(w*0.46), int(w*0.74), int(w*0.46))

    # Star / Verified Badge (Bottom Right)
    painter.setPen(QPen(QColor("#60A5FA"), 1.5))
    painter.setBrush(QBrush(QColor("#3B82F6")))
    check_path = QPainterPath()
    check_path.moveTo(w*0.56, w*0.68)
    check_path.lineTo(w*0.64, w*0.76)
    check_path.lineTo(w*0.78, w*0.58)
    painter.drawPath(check_path)

    painter.end()
    return pix


def draw_ocr_pixmap(size=32, color_hex="#3B82F6"):
    """Realistic HD Blue Vector Icon for OCR Reader."""
    pix = _create_base_pixmap(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    w = size
    col = QColor(color_hex)

    # Base Document Page with Folded Corner
    painter.setPen(QPen(QColor("#2563EB"), 2))
    painter.setBrush(QBrush(QColor(30, 58, 138, 50)))
    doc_path = QPainterPath()
    doc_path.moveTo(w*0.2, w*0.14)
    doc_path.lineTo(w*0.6, w*0.14)
    doc_path.lineTo(w*0.8, w*0.34)
    doc_path.lineTo(w*0.8, w*0.86)
    doc_path.lineTo(w*0.2, w*0.86)
    doc_path.closeSubpath()
    painter.drawPath(doc_path)

    # Fold Corner
    painter.drawLine(int(w*0.6), int(w*0.14), int(w*0.6), int(w*0.34))
    painter.drawLine(int(w*0.6), int(w*0.34), int(w*0.8), int(w*0.34))

    # OCR Document Text Lines
    painter.setPen(QPen(QColor("#93C5FD"), 1.8))
    painter.drawLine(int(w*0.3), int(w*0.4), int(w*0.7), int(w*0.4))
    painter.drawLine(int(w*0.3), int(w*0.52), int(w*0.7), int(w*0.52))
    painter.drawLine(int(w*0.3), int(w*0.64), int(w*0.6), int(w*0.64))
    painter.drawLine(int(w*0.3), int(w*0.74), int(w*0.5), int(w*0.74))

    # Laser Beam Scanner Line across Middle (Glowing Blue)
    painter.setPen(QPen(QColor("#38BDF8"), 2.2))
    painter.drawLine(int(w*0.12), int(w*0.52), int(w*0.88), int(w*0.52))

    # Corner Scanning Target Brackets [ ]
    painter.setPen(QPen(QColor("#60A5FA"), 2))
    d = w * 0.14
    # Top-Left Bracket
    painter.drawLine(int(w*0.12), int(w*0.2), int(w*0.12 + d), int(w*0.2))
    painter.drawLine(int(w*0.12), int(w*0.2), int(w*0.12), int(w*0.2 + d))
    # Bottom-Right Bracket
    painter.drawLine(int(w*0.88), int(w*0.8), int(w*0.88 - d), int(w*0.8))
    painter.drawLine(int(w*0.88), int(w*0.8), int(w*0.88), int(w*0.8 - d))

    painter.end()
    return pix


def draw_pdf_pixmap(size=32, color_hex="#3B82F6"):
    """Realistic HD Blue Vector Icon for PDF Analyzer."""
    pix = _create_base_pixmap(size)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    w = size
    col = QColor(color_hex)

    # Shadow Layer (Second Page behind)
    painter.setPen(QPen(QColor("#1D4ED8"), 1.5))
    painter.setBrush(QBrush(QColor(29, 78, 216, 30)))
    painter.drawRoundedRect(QRectF(w*0.26, w*0.22, w*0.6, w*0.7), 5, 5)

    # Front Main PDF Document Page
    painter.setPen(QPen(QColor("#3B82F6"), 2))
    painter.setBrush(QBrush(QColor(30, 58, 138, 70)))
    main_doc = QPainterPath()
    main_doc.moveTo(w*0.14, w*0.12)
    main_doc.lineTo(w*0.54, w*0.12)
    main_doc.lineTo(w*0.72, w*0.3)
    main_doc.lineTo(w*0.72, w*0.82)
    main_doc.lineTo(w*0.14, w*0.82)
    main_doc.closeSubpath()
    painter.drawPath(main_doc)

    # Fold Corner
    painter.drawLine(int(w*0.54), int(w*0.12), int(w*0.54), int(w*0.3))
    painter.drawLine(int(w*0.54), int(w*0.3), int(w*0.72), int(w*0.3))

    # PDF Red/Blue Emblem Header Banner
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(QColor("#2563EB")))
    painter.drawRoundedRect(QRectF(w*0.22, w*0.38, w*0.42, w*0.16), 3, 3)

    # Text Lines
    painter.setPen(QPen(QColor("#93C5FD"), 1.8))
    painter.drawLine(int(w*0.22), int(w*0.62), int(w*0.64), int(w*0.62))
    painter.drawLine(int(w*0.22), int(w*0.72), int(w*0.52), int(w*0.72))

    # AI Analyzer Spark / Lens Accent (Bottom Right)
    painter.setPen(QPen(QColor("#38BDF8"), 2))
    painter.drawEllipse(QPointF(w*0.64, w*0.68), w*0.12, w*0.12)
    painter.drawLine(int(w*0.72), int(w*0.76), int(w*0.84), int(w*0.88))

    painter.end()
    return pix


def draw_code_pixmap(size=32, color_hex="#3B82F6"):
    return draw_interview_prep_pixmap(size, color_hex)

def get_tab_icon(tab_name):
    name = tab_name.lower()
    if "dash" in name:
        return draw_dashboard_icon()
    elif "voice" in name:
        return draw_voice_icon()
    elif "chat" in name:
        return draw_chat_icon()
    elif "vision" in name:
        return draw_vision_icon()
    elif "doc" in name:
        return draw_doc_icon()
    elif "sec" in name:
        return draw_security_icon()
    elif "analyt" in name:
        return draw_analytics_icon()
    elif "set" in name:
        return draw_settings_icon()
    else:
        return draw_dashboard_icon()

def get_card_icon_pixmap(key, size=32, color_hex=None):
    k = key.lower()
    if "search" in k:
        return draw_search_pixmap(size, color_hex or "#94A3B8")
    elif "bell" in k or "notif" in k:
        return draw_bell_pixmap(size, color_hex or "#60A5FA")
    elif "user" in k or "avatar" in k:
        return draw_user_pixmap(size, color_hex or "#3B82F6")
    elif "check" in k or "task" in k:
        return draw_check_pixmap(size, color_hex or "#10B981")
    elif "folder" in k or "file" in k or "dup" in k:
        return draw_folder_pixmap(size, color_hex or "#60A5FA")
    elif "code" in k or "dev" in k or "interview" in k or "prep" in k:
        return draw_interview_prep_pixmap(size, color_hex or "#3B82F6")
    elif "voice" in k or "mic" in k:
        return draw_voice_icon(size, color_hex or "#10B981").pixmap(size, size)
    elif "shield" in k or "sec" in k or "up" in k:
        return draw_security_icon(size, color_hex or "#EF4444").pixmap(size, size)
    elif "face" in k or "scan" in k:
        return draw_vision_icon(size, color_hex or "#60A5FA").pixmap(size, size)
    elif "ocr" in k:
        return draw_ocr_pixmap(size, color_hex or "#3B82F6")
    elif "pdf" in k or "doc" in k:
        return draw_pdf_pixmap(size, color_hex or "#3B82F6")
    else:
        return draw_dashboard_icon(size, color_hex or "#3B82F6").pixmap(size, size)

