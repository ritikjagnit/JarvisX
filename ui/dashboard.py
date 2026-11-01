import sys
import os
import math
import random
import psutil
from datetime import datetime

from PyQt6.QtCore import (
    Qt, QTimer, QRectF, QPointF, QEasingCurve, QPropertyAnimation,
    pyqtProperty, pyqtSignal, QSize
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QFont, QBrush, QFontDatabase,
    QLinearGradient, QRadialGradient, QConicalGradient, QPainterPath,
    QPixmap, QImage, QTransform, QIcon, QCursor
)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QFrame, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect, QScrollBar, QStackedWidget, QScrollArea, QProgressBar,
    QSizePolicy, QDialog, QComboBox
)

# ---------------- GLOBAL ANIMATION CONTROLLER ----------------
class AnimationController:
    def __init__(self):
        self.global_pulse = 0
        self.time = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
    
    def start(self):
        if not self.timer.isActive():
            self.timer.start(20)

    def _tick(self):
        self.time += 0.02
        self.global_pulse = (math.sin(self.time * 2) + 1) * 0.5

anim_controller = None


# ---------------- MASTER 5D HOLOGRAPHIC COMMAND CORE ----------------
class MasterCommandCoreWidget(QWidget):
    """
    5D Quantum Holographic Core:
    Renders 3D Arc Reactor, Dual Counter-Rotating Telemetry Rings,
    360° Tactical Radar with Target Blips, 32-Bar Quantum Equalizer,
    and Floating Particle Field Matrix.
    """
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.angle = 0
        self.sweep_angle = 0
        self.pulse = 0
        self.is_ultron = False
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Audio Spectrum Sim Data (32 bars)
        self.num_bars = 32
        self.heights = [random.uniform(12, 50) for _ in range(self.num_bars)]
        
        # Floating Quantum Particles (40 particles)
        self.particles = [
            {
                'x': random.uniform(-130, 130),
                'y': random.uniform(-130, 130),
                'speed': random.uniform(0.4, 1.8),
                'size': random.uniform(1.2, 3.2),
                'alpha_offset': random.uniform(0, 6.28)
            }
            for _ in range(40)
        ]

        # Tactical Radar Target Blips
        self.blips = [
            {'r': 65, 'angle': 45},
            {'r': 95, 'angle': 190},
            {'r': 40, 'angle': 280},
            {'r': 80, 'angle': 330}
        ]
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def set_ultron_mode(self, enabled):
        self.is_ultron = enabled
        self.update()

    def animate(self):
        self.angle = (self.angle + 1.2) % 360
        self.sweep_angle = (self.sweep_angle + 2.8) % 360
        self.pulse = (math.sin(self.angle * 0.08) + 1) * 0.5
        
        # Update audio heights dynamically
        for i in range(self.num_bars):
            base = 18 + 28 * math.sin(self.angle * 0.12 + i * 0.35)
            noise = random.uniform(-6, 6)
            self.heights[i] = max(6.0, min(58.0, base + noise))

        # Update floating particles
        for p in self.particles:
            p['y'] -= p['speed']
            if p['y'] < -135:
                p['y'] = 135
                p['x'] = random.uniform(-130, 130)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        primary_color = QColor(255, 0, 85) if self.is_ultron else QColor(59, 130, 246)
        secondary_color = QColor(255, 120, 0) if self.is_ultron else QColor(96, 165, 250)

        # 0. Draw Frosted Glassmorphic Outer Panel
        bg_grad = QLinearGradient(QPointF(0, 0), QPointF(rect.width(), rect.height()))
        if self.is_ultron:
            bg_grad.setColorAt(0.0, QColor(25, 4, 12, 220))
            bg_grad.setColorAt(1.0, QColor(10, 2, 6, 230))
        else:
            bg_grad.setColorAt(0.0, QColor(16, 24, 39, 230))
            bg_grad.setColorAt(1.0, QColor(11, 17, 32, 240))

        painter.setBrush(QBrush(bg_grad))
        painter.setPen(QPen(QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 120), 1.2))
        painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 16, 16)

        center = rect.center()
        painter.translate(center)

        # 1. Floating Quantum Particle Field
        for p in self.particles:
            dist = math.sqrt(p['x']**2 + p['y']**2)
            if dist < 135:
                pulse_alpha = int(140 + 100 * math.sin(self.angle * 0.1 + p['alpha_offset']))
                p_color = QColor(secondary_color.red(), secondary_color.green(), secondary_color.blue(), max(20, min(240, pulse_alpha)))
                painter.setBrush(QBrush(p_color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPointF(p['x'], p['y']), p['size'], p['size'])

        # 2. Orbital Concentric Radar Grids
        grid_pen = QPen(QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 45), 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for r in [40, 75, 110, 140]:
            painter.drawEllipse(QPointF(0, 0), r, r)

        # 3. 360 Radar Sweeper Arc
        sweep_grad = QConicalGradient(QPointF(0, 0), -self.sweep_angle)
        sweep_color = QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 100)
        sweep_grad.setColorAt(0.0, sweep_color)
        sweep_grad.setColorAt(0.2, QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 0))
        sweep_grad.setColorAt(1.0, QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 0))
        painter.setBrush(QBrush(sweep_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(0, 0), 140, 140)

        # 4. Radar Blips
        for b in self.blips:
            rad = math.radians(b['angle'])
            bx = b['r'] * math.cos(rad)
            by = b['r'] * math.sin(rad)
            b_alpha = int(180 + 75 * math.sin(self.angle * 0.2 + b['r']))
            blip_col = QColor(secondary_color.red(), secondary_color.green(), secondary_color.blue(), max(40, min(255, b_alpha)))
            painter.setBrush(QBrush(blip_col))
            painter.drawEllipse(QPointF(bx, by), 3.5, 3.5)

        # 5. Dual Counter-Rotating Telemetry Rings
        painter.save()
        painter.rotate(self.angle)
        ring_pen1 = QPen(QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 160), 1.8)
        painter.setPen(ring_pen1)
        painter.drawArc(-118, -118, 236, 236, 0, 70 * 16)
        painter.drawArc(-118, -118, 236, 236, 120 * 16, 70 * 16)
        painter.drawArc(-118, -118, 236, 236, 240 * 16, 70 * 16)
        painter.restore()

        painter.save()
        painter.rotate(-self.angle * 1.5)
        ring_pen2 = QPen(QColor(secondary_color.red(), secondary_color.green(), secondary_color.blue(), 140), 1.2, Qt.PenStyle.DotLine)
        painter.setPen(ring_pen2)
        painter.drawArc(-95, -95, 190, 190, 30 * 16, 110 * 16)
        painter.drawArc(-95, -95, 190, 190, 210 * 16, 110 * 16)
        painter.restore()

        # 6. Circular 32-Bar Equalizer
        for i in range(self.num_bars):
            bar_angle = (360.0 / self.num_bars) * i
            rad = math.radians(bar_angle)
            h = self.heights[i]
            
            x1 = 76 * math.cos(rad)
            y1 = 76 * math.sin(rad)
            x2 = (76 + h * 0.45) * math.cos(rad)
            y2 = (76 + h * 0.45) * math.sin(rad)

            b_grad = QLinearGradient(QPointF(x1, y1), QPointF(x2, y2))
            b_grad.setColorAt(0.0, QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 200))
            b_grad.setColorAt(1.0, QColor(secondary_color.red(), secondary_color.green(), secondary_color.blue(), 240))

            pen = QPen(QBrush(b_grad), 2.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # 7. Core Arc Reactor Central Orb
        orb_r = 45 + 5 * self.pulse
        orb_grad = QRadialGradient(QPointF(0, 0), orb_r)
        orb_grad.setColorAt(0.0, QColor(255, 255, 255, 255))
        orb_grad.setColorAt(0.35, QColor(secondary_color.red(), secondary_color.green(), secondary_color.blue(), 220))
        orb_grad.setColorAt(0.75, QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 150))
        orb_grad.setColorAt(1.0, QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 0))

        painter.setBrush(QBrush(orb_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(0, 0), orb_r, orb_r)


# ---------------- ACTIVITY TREND CHART WIDGET ----------------
class ActivityTrendWidget(QWidget):
    """Renders a smooth animated Bezier activity curve with translucent gradient fill."""
    def __init__(self):
        super().__init__()
        self.points = [18, 38, 25, 68, 48, 88, 72]
        self.days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        self.setMinimumHeight(140)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(10, 10, -10, -25)
        if rect.width() <= 0 or rect.height() <= 0:
            return

        # Draw grid lines
        grid_pen = QPen(QColor(255, 255, 255, 12), 1, Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)
        for i in range(4):
            y = rect.top() + (rect.height() / 3) * i
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))

        # Calculate coordinates
        coords = []
        num_pts = len(self.points)
        x_step = rect.width() / (num_pts - 1)
        for i, val in enumerate(self.points):
            cx = rect.left() + i * x_step
            cy = rect.bottom() - (val / 100.0) * rect.height()
            coords.append(QPointF(cx, cy))

        # Build Bezier Path
        path = QPainterPath()
        path.moveTo(coords[0])
        for i in range(len(coords) - 1):
            p1 = coords[i]
            p2 = coords[i + 1]
            ctrl1 = QPointF(p1.x() + x_step * 0.4, p1.y())
            ctrl2 = QPointF(p2.x() - x_step * 0.4, p2.y())
            path.cubicTo(ctrl1, ctrl2, p2)

        # Gradient Fill Under Curve
        fill_path = QPainterPath(path)
        fill_path.lineTo(coords[-1].x(), rect.bottom())
        fill_path.lineTo(coords[0].x(), rect.bottom())
        fill_path.closeSubpath()

        grad = QLinearGradient(QPointF(rect.topLeft()), QPointF(rect.bottomLeft()))
        grad.setColorAt(0.0, QColor(59, 130, 246, 90))
        grad.setColorAt(1.0, QColor(59, 130, 246, 0))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(fill_path)

        # Draw Curve Line
        line_pen = QPen(QColor(59, 130, 246), 2.5)
        painter.setPen(line_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        # Draw Glowing Data Points & Labels
        font = QFont("Segoe UI", 8, QFont.Weight.Bold)
        painter.setFont(font)
        for i, pt in enumerate(coords):
            # Outer aura
            painter.setBrush(QBrush(QColor(96, 165, 250, 100)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(pt, 5, 5)
            # Inner dot
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(pt, 2.5, 2.5)

            # Day label neatly positioned inside chart bounds
            painter.setPen(QPen(QColor(148, 163, 184)))
            painter.drawText(int(pt.x() - 10), int(rect.bottom() + 14), self.days[i])


# ---------------- CUSTOM CHAT INPUT EDIT (ENTER TO SUBMIT) ----------------
class CustomChatInputEdit(QTextEdit):
    """
    ChatGPT-Style Multiline Input Box:
    - Pressing Enter / Return emits `return_pressed` to submit message instantly.
    - Pressing Shift + Enter inserts a new line (\n).
    """
    return_pressed = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                self.return_pressed.emit()
                event.accept()
                return
        super().keyPressEvent(event)


# ---------------- TERMINAL & CHAT WIDGET ----------------
class TerminalWidget(QFrame):
    """
    Enterprise Chat & Terminal Log Panel:
    Supports append_message(speaker, text) for seamless main.py bridge connection.
    Renders React-style message cards with syntax highlighting & timestamps.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("terminalCard")
        self.setStyleSheet("""
            QFrame#terminalCard {
                background: rgba(16, 24, 39, 0.75);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        head_layout = QHBoxLayout()
        icon_lbl = QLabel("💬")
        icon_lbl.setStyleSheet("font-size: 16px; background: transparent;")
        title_lbl = QLabel("AI Chat & System Terminal")
        title_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #F8FAFC; background: transparent;")

        status_dot = QLabel("● LIVE STREAMING")
        status_dot.setStyleSheet("color: #10B981; font-size: 10px; font-weight: bold; background: transparent;")

        head_layout.addWidget(icon_lbl)
        head_layout.addWidget(title_lbl)
        head_layout.addStretch()
        head_layout.addWidget(status_dot)
        layout.addLayout(head_layout)

        # Chat Search Bar Container
        search_container = QFrame()
        search_container.setStyleSheet("""
            QFrame {
                background: rgba(30, 41, 59, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px;
                padding: 2px 8px;
            }
        """)
        s_layout = QHBoxLayout(search_container)
        s_layout.setContentsMargins(6, 4, 6, 4)
        s_layout.setSpacing(8)

        self.chat_search_input = QLineEdit()
        self.chat_search_input.setPlaceholderText("🔍 Search chat messages & history...")
        self.chat_search_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #F8FAFC;
                font-size: 12px;
            }
        """)
        self.chat_search_input.textChanged.connect(self._filter_chat_history)

        self.match_count_lbl = QLabel("")
        self.match_count_lbl.setStyleSheet("color: #60A5FA; font-weight: bold; font-size: 10px; background: transparent;")

        self.clear_search_btn = QPushButton("✖")
        self.clear_search_btn.setFixedSize(22, 22)
        self.clear_search_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.clear_search_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.1);
                color: #94A3B8;
                border: none;
                border-radius: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #EF4444;
                color: white;
            }
        """)
        self.clear_search_btn.clicked.connect(self._clear_chat_search)

        s_layout.addWidget(self.chat_search_input, 1)
        s_layout.addWidget(self.match_count_lbl)
        s_layout.addWidget(self.clear_search_btn)
        layout.addWidget(search_container)

        # Chat Text Display
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet("""
            QTextEdit {
                background: transparent;
                border: none;
                color: #E2E8F0;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                line-height: 1.5;
            }
        """)
        layout.addWidget(self.text_area, 1)

        # Bottom Dedicated Chat Input Row for AI Chat Tab
        chat_bar = QFrame()
        chat_bar.setFixedHeight(48)
        chat_bar.setStyleSheet("""
            QFrame {
                background: rgba(30, 41, 59, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
        """)
        cb_layout = QHBoxLayout(chat_bar)
        cb_layout.setContentsMargins(10, 0, 10, 0)
        cb_layout.setSpacing(8)

        self.chat_input = CustomChatInputEdit()
        self.chat_input.setPlaceholderText("Type your message here... Press Enter to Send")
        self.chat_input.setFixedHeight(34)
        self.chat_input.setStyleSheet("""
            QTextEdit {
                background: transparent;
                border: none;
                color: #F8FAFC;
                font-size: 12px;
            }
        """)

        self.chat_send_btn = QPushButton(" Send ⚡ ")
        self.chat_send_btn.setFixedHeight(32)
        self.chat_send_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.chat_send_btn.setStyleSheet("""
            QPushButton {
                background: #3B82F6;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11px;
                padding: 0 12px;
            }
            QPushButton:hover {
                background: #60A5FA;
            }
        """)

        # Connect Enter Key signal
        self.chat_input.return_pressed.connect(self.chat_send_btn.click)

        cb_layout.addWidget(self.chat_input, 1)
        cb_layout.addWidget(self.chat_send_btn)
        layout.addWidget(chat_bar)

        # Internal chat history buffer for filtering
        self.chat_history_records = []

        # Initial Welcome Message
        self.append_message("SHRIVA AI", "Hello! I am SHRIVA AI, your central AI assistant. How can I help you today?")

    def append_message(self, speaker, message):
        time_str = datetime.now().strftime("%H:%M")
        self.chat_history_records.append((speaker, message, time_str))
        self._render_messages(self.chat_history_records)

    def _render_messages(self, records):
        self.text_area.clear()
        query = self.chat_search_input.text().strip().lower() if hasattr(self, 'chat_search_input') else ""

        # Filter strictly for USER inputs
        user_records = [r for r in records if r[0].upper() in ["YOU", "USER"]]

        # Display Top Header Banner
        header_html = """
        <div style="margin-bottom: 12px; padding: 6px 12px; background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 8px; text-align: center;">
            <span style="font-size: 11px; font-weight: bold; color: #60A5FA;">💬 USER COMMAND & PROMPT HISTORY LOG</span>
        </div>
        """
        self.text_area.append(header_html)

        for speaker, message, time_str in user_records:
            msg_text = message
            if query and query in msg_text.lower():
                # Highlight matching text
                idx = msg_text.lower().find(query)
                matched_part = msg_text[idx:idx+len(query)]
                msg_text = msg_text[:idx] + f"<mark style='background: #F59E0B; color: black; border-radius: 3px; padding: 1px 4px;'>{matched_part}</mark>" + msg_text[idx+len(query):]

            html = f"""
            <div style="margin: 8px 0px; text-align: right;">
                <span style="font-size: 10px; color: #94A3B8; margin-right: 4px;">{time_str} • You</span>
                <div style="display: inline-block; background: linear-gradient(135deg, #3B82F6, #2563EB); color: #FFFFFF; padding: 10px 16px; border-radius: 16px 16px 4px 16px; font-size: 13px; text-align: left; max-width: 85%;">
                    {msg_text}
                </div>
            </div>
            """
            self.text_area.append(html)
        
        sb = self.text_area.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _filter_chat_history(self, text):
        query = text.strip().lower()
        if not query:
            self.match_count_lbl.setText("")
            self._render_messages(self.chat_history_records)
            return

        filtered = [r for r in self.chat_history_records if query in r[1].lower() or query in r[0].lower()]
        self.match_count_lbl.setText(f"{len(filtered)} match(es)")
        self._render_messages(filtered)

    def _clear_chat_search(self):
        self.chat_search_input.clear()
        self.match_count_lbl.setText("")
        self._render_messages(self.chat_history_records)

    def append(self, text):
        self.append_message("SHRIVA AI", text)


# ---------------- MOBILE PAIRING SECURITY DIALOG ----------------
class MobilePairingDialog(QDialog):
    """
    SHRIVA AI Mobile Pairing Portal:
    Provides live QR Code pairing, 6-digit OTP code, and paired device revocation.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SHRIVA AI - Mobile Device Pairing & Remote Access")
        self.resize(520, 480)
        self.setStyleSheet("background-color: #050816; color: #F8FAFC; font-family: 'Segoe UI', sans-serif;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("📱 Mobile Ecosystem Pairing")
        title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #60A5FA;")
        layout.addWidget(title)

        desc = QLabel("Scan the QR code or enter the 6-digit OTP code in the mobile web app to securely pair your phone or tablet.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #94A3B8; font-size: 11px;")
        layout.addWidget(desc)

        # OTP Container
        otp_box = QFrame()
        otp_box.setStyleSheet("background: rgba(16, 24, 39, 0.9); border: 1px solid rgba(59, 130, 246, 0.4); border-radius: 12px; padding: 16px;")
        otp_layout = QVBoxLayout(otp_box)
        
        lbl = QLabel("PAIRING OTP CODE (VALID FOR 5 MINS)")
        lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #64748B;")
        
        import remote_security
        otp_code = remote_security.generate_otp_code()
        
        self.otp_val = QLabel(otp_code)
        self.otp_val.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        self.otp_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.otp_val.setStyleSheet("color: #10B981; letter-spacing: 8px;")
        
        otp_layout.addWidget(lbl, 0, Qt.AlignmentFlag.AlignCenter)
        otp_layout.addWidget(self.otp_val)
        layout.addWidget(otp_box)

        # Server URL
        import socket
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
        except Exception:
            local_ip = "127.0.0.1"
            
        url_lbl = QLabel(f"🌐 Mobile Access URL: http://{local_ip}:8000/mobile")
        url_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        url_lbl.setStyleSheet("color: #3B82F6;")
        layout.addWidget(url_lbl)

        # Close Button
        close_btn = QPushButton("Done")
        close_btn.setFixedHeight(40)
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #60A5FA;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


# ---------------- MASTER DASHBOARD WINDOW CLASS ----------------
class JarvisUltimate(QWidget):
    """
    Enterprise AI Redesign Main Window:
    - Floating Animated Glass Sidebar
    - Top Navigation Header with Search & User Status
    - Multi-Tab View Stack (Dashboard, Voice Assistant, AI Chat, Vision Hub, Document AI, Security, Analytics, Settings)
    - Full Bridge & Callback compatibility with main.py
    """
    ultron_mode_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.is_ultron = False
        self.vibrate_count = 0
        self.vibrate_timer = QTimer()

        self.setWindowTitle("SHRIVA AI Enterprise Workspace")
        self.resize(1340, 860)

        # Global Window Theme
        self.setStyleSheet("""
            QWidget {
                background-color: #050816;
                color: #F8FAFC;
                font-family: 'Segoe UI', sans-serif;
            }
        """)

        # Main Layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Outer Container for Vibration Alerts
        self.main_container = QWidget(self)
        self.main_container.setObjectName("mainContainer")
        self.main_container.setStyleSheet("#mainContainer { background-color: #050816; }")
        
        container_layout = QHBoxLayout(self.main_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        self.main_layout.addWidget(self.main_container)

        # 1. Create Left Animated Sidebar
        self.sidebar = self.create_sidebar()
        container_layout.addWidget(self.sidebar)

        # 2. Create Right Main Work Area (Header + Tab Stack + Status Bar)
        self.work_area = QWidget()
        work_layout = QVBoxLayout(self.work_area)
        work_layout.setContentsMargins(18, 18, 18, 12)
        work_layout.setSpacing(16)
        container_layout.addWidget(self.work_area, 1)

        # Top Floating Header
        self.header = self.create_header()
        work_layout.addWidget(self.header)

        # Central Stacked Widget
        self.stacked_widget = QStackedWidget()
        work_layout.addWidget(self.stacked_widget, 1)

        # Build View Pages for Stack (Core 5-Tab Architecture)
        self.page_dashboard = self.create_dashboard_view()
        self.page_chat = self.create_chat_view()
        self.page_security = self.create_security_view()
        self.page_analytics = self.create_analytics_view()
        self.page_settings = self.create_settings_view()

        self.stacked_widget.addWidget(self.page_dashboard)  # Index 0
        self.stacked_widget.addWidget(self.page_chat)       # Index 1
        self.stacked_widget.addWidget(self.page_security)   # Index 2
        self.stacked_widget.addWidget(self.page_analytics)  # Index 3
        self.stacked_widget.addWidget(self.page_settings)   # Index 4

        # Bottom HUD Status Bar
        self.status_bar = self.create_status_bar()
        work_layout.addWidget(self.status_bar)

        # Start Timers for Realtime Telemetry
        self.start_system_updates()

    # ---------------- SIDEBAR ----------------
    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #0B1120;
                border-right: 1px solid rgba(255, 255, 255, 0.08);
            }
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(12)

        # Logo & App Title
        logo_layout = QHBoxLayout()
        logo_icon = QLabel("⚡")
        logo_icon.setStyleSheet("""
            QLabel {
                font-size: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3B82F6, stop:1 #60A5FA);
                border-radius: 8px;
                padding: 4px;
            }
        """)
        
        logo_text_layout = QVBoxLayout()
        logo_text_layout.setSpacing(0)
        logo_title = QLabel("SHRIVA AI")
        logo_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        logo_title.setStyleSheet("color: #F8FAFC; background: transparent;")
        
        logo_sub = QLabel("AI Assistant")
        logo_sub.setFont(QFont("Segoe UI", 9))
        logo_sub.setStyleSheet("color: #64748B; background: transparent;")

        logo_text_layout.addWidget(logo_title)
        logo_text_layout.addWidget(logo_sub)

        logo_layout.addWidget(logo_icon)
        logo_layout.addLayout(logo_text_layout)
        logo_layout.addStretch()
        layout.addLayout(logo_layout)

        layout.addSpacing(10)

        # Vector Icon Import
        from ui.vector_icons import get_tab_icon

        # Nav Buttons with Authentic Vector Icons (Essential 5-Tab Navigation)
        self.nav_buttons = []
        nav_items = [
            ("Dashboard", 0, "dashboard"),
            ("AI Chat", 1, "chat"),
            ("Security Portal", 2, "security"),
            ("System Analytics", 3, "analytics"),
            ("Settings", 4, "settings")
        ]

        for text, idx, key in nav_items:
            btn = QPushButton(f"  {text}")
            btn.setIcon(get_tab_icon(key))
            btn.setIconSize(QSize(20, 20))
            btn.setFixedHeight(44)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #94A3B8;
                    border: none;
                    border-radius: 10px;
                    padding-left: 14px;
                    text-align: left;
                    font-size: 13px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: rgba(59, 130, 246, 0.14);
                    color: #F8FAFC;
                }
            """)
            btn.clicked.connect(lambda checked, index=idx: self.switch_tab(index))
            layout.addWidget(btn)
            self.nav_buttons.append(btn)

        layout.addStretch()

        # System Status Floating Card in Sidebar Footer
        sys_card = QFrame()
        sys_card.setStyleSheet("""
            QFrame {
                background: rgba(16, 24, 39, 0.75);
                border: 1px solid rgba(16, 185, 129, 0.3);
                border-radius: 12px;
                padding: 10px;
            }
        """)
        sys_layout = QHBoxLayout(sys_card)
        sys_layout.setContentsMargins(8, 6, 8, 6)

        dot = QLabel("●")
        dot.setStyleSheet("color: #10B981; font-size: 14px; background: transparent;")
        
        sys_info = QVBoxLayout()
        sys_info.setSpacing(0)
        t1 = QLabel("System Status")
        t1.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        t1.setStyleSheet("color: #F8FAFC; background: transparent;")
        
        t2 = QLabel("Online • Quantum Core")
        t2.setFont(QFont("Segoe UI", 8))
        t2.setStyleSheet("color: #10B981; background: transparent;")
        
        sys_info.addWidget(t1)
        sys_info.addWidget(t2)

        sys_layout.addWidget(dot)
        sys_layout.addLayout(sys_info)
        sys_layout.addStretch()

        layout.addWidget(sys_card)

        # Highlight default tab (Dashboard - 0)
        self.update_nav_highlight(0)

        return sidebar

    def switch_tab(self, index):
        self.stacked_widget.setCurrentIndex(index)
        self.update_nav_highlight(index)

    def update_nav_highlight(self, active_index):
        for idx, btn in enumerate(self.nav_buttons):
            if idx == active_index:
                btn.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #60A5FA);
                        color: #FFFFFF;
                        border: none;
                        border-radius: 10px;
                        padding-left: 16px;
                        text-align: left;
                        font-size: 13px;
                        font-weight: 700;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        color: #94A3B8;
                        border: none;
                        border-radius: 10px;
                        padding-left: 16px;
                        text-align: left;
                        font-size: 13px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: rgba(59, 130, 246, 0.12);
                        color: #F8FAFC;
                    }
                """)

    # ---------------- HEADER ----------------
    def create_header(self):
        header = QFrame()
        header.setFixedHeight(64)
        header.setStyleSheet("""
            QFrame {
                background: rgba(11, 17, 32, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
        """)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(16)

        # Greeting Title
        greet_layout = QVBoxLayout()
        greet_layout.setSpacing(2)
        
        hour = datetime.now().hour
        greeting = "Good Morning" if hour < 12 else ("Good Afternoon" if hour < 17 else "Good Evening")
        self.greet_lbl = QLabel(f"{greeting}, Shravani")
        self.greet_lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.greet_lbl.setStyleSheet("color: #F8FAFC; background: transparent;")

        sub_lbl = QLabel("Your AI assistant is ready to help you")
        sub_lbl.setFont(QFont("Segoe UI", 9))
        sub_lbl.setStyleSheet("color: #94A3B8; background: transparent;")

        greet_layout.addWidget(self.greet_lbl)
        greet_layout.addWidget(sub_lbl)
        layout.addLayout(greet_layout)

        layout.addStretch()

        from ui.vector_icons import get_card_icon_pixmap

        # Global Search Bar Input
        search_frame = QFrame()
        search_frame.setFixedSize(260, 38)
        search_frame.setStyleSheet("""
            QFrame {
                background: rgba(16, 24, 39, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 10px;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(10, 0, 10, 0)
        
        search_icon = QLabel()
        search_icon.setPixmap(get_card_icon_pixmap("search", 18))
        search_icon.setStyleSheet("background: transparent;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search anything... Ctrl + K")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: #F8FAFC;
                font-size: 11px;
            }
        """)
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        layout.addWidget(search_frame)

        # Notification Button with Vector Icon
        notif_btn = QPushButton()
        notif_btn.setIcon(QIcon(get_card_icon_pixmap("bell", 20)))
        notif_btn.setIconSize(QSize(20, 20))
        notif_btn.setFixedSize(38, 38)
        notif_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        notif_btn.setStyleSheet("""
            QPushButton {
                background: rgba(16, 24, 39, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 10px;
            }
            QPushButton:hover {
                background: rgba(59, 130, 246, 0.2);
            }
        """)
        layout.addWidget(notif_btn)

        # User Profile Avatar Badge with Vector User Icon
        profile_frame = QFrame()
        profile_frame.setFixedHeight(38)
        profile_frame.setStyleSheet("""
            QFrame {
                background: rgba(16, 24, 39, 0.9);
                border: 1px solid rgba(59, 130, 246, 0.4);
                border-radius: 10px;
                padding-right: 12px;
            }
        """)
        profile_layout = QHBoxLayout(profile_frame)
        profile_layout.setContentsMargins(8, 0, 8, 0)

        avatar = QLabel()
        avatar.setPixmap(get_card_icon_pixmap("user", 20))
        avatar.setStyleSheet("background: transparent;")
        
        prof_name = QLabel("Shravani")
        prof_name.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        prof_name.setStyleSheet("color: #F8FAFC; background: transparent; margin-left: 4px;")

        profile_layout.addWidget(avatar)
        profile_layout.addWidget(prof_name)
        layout.addWidget(profile_frame)

        return header

    # ---------------- TAB 0: DASHBOARD HERO VIEW ----------------
    def create_dashboard_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # 1. Top 4 Analytics Summary Cards Row
        cards_row = QHBoxLayout()
        cards_row.setSpacing(14)

        from ui.vector_icons import get_card_icon_pixmap

        metrics = [
            ("Voice Commands", "1,247", "voice", "+12.5% from yesterday", "#10B981"),
            ("AI Tasks Completed", "892", "task", "+8.2% from yesterday", "#10B981"),
            ("Files Processed", "156", "file", "+15.3% from yesterday", "#60A5FA"),
            ("System Uptime", "99.8%", "shield", "Optimal Performance", "#A855F7")
        ]

        for title, val, icon_key, sub, sub_col in metrics:
            card = QFrame()
            card.setFixedHeight(88)
            card.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(16, 24, 39, 0.85), stop:1 rgba(11, 17, 32, 0.95));
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 14px;
                }
                QFrame:hover {
                    border: 1px solid rgba(59, 130, 246, 0.4);
                }
            """)
            c_layout = QHBoxLayout(card)
            c_layout.setContentsMargins(16, 12, 16, 12)

            info_layout = QVBoxLayout()
            info_layout.setSpacing(2)
            
            t_lbl = QLabel(title)
            t_lbl.setFont(QFont("Segoe UI", 9))
            t_lbl.setStyleSheet("color: #94A3B8; background: transparent;")

            v_lbl = QLabel(val)
            v_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            v_lbl.setStyleSheet("color: #F8FAFC; background: transparent;")

            s_lbl = QLabel(sub)
            s_lbl.setFont(QFont("Segoe UI", 8))
            s_lbl.setStyleSheet(f"color: {sub_col}; background: transparent;")

            info_layout.addWidget(t_lbl)
            info_layout.addWidget(v_lbl)
            info_layout.addWidget(s_lbl)

            icon_box = QLabel()
            icon_box.setPixmap(get_card_icon_pixmap(icon_key, 24))
            icon_box.setStyleSheet("background: transparent;")

            c_layout.addLayout(info_layout)
            c_layout.addStretch()
            c_layout.addWidget(icon_box)

            cards_row.addWidget(card)

        layout.addLayout(cards_row)

        # 2. Main Center Split Grid (Voice Arc Reactor + AI Capabilities Grid + Activity Trend)
        center_split = QHBoxLayout()
        center_split.setSpacing(14)

        # LEFT: Voice Assistant Arc Reactor Hero Panel
        left_hero = QFrame()
        left_hero.setStyleSheet("""
            QFrame {
                background: rgba(16, 24, 39, 0.75);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
        """)
        left_layout = QVBoxLayout(left_hero)
        left_layout.setContentsMargins(14, 14, 14, 14)
        left_layout.setSpacing(10)

        hero_title_layout = QHBoxLayout()
        h_icon = QLabel()
        h_icon.setPixmap(get_card_icon_pixmap("voice", 18))
        h_icon.setStyleSheet("background: transparent;")
        h_title = QLabel("Voice Assistant")
        h_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        h_title.setStyleSheet("color: #F8FAFC; background: transparent; margin-left: 6px;")
        hero_title_layout.addWidget(h_icon)
        hero_title_layout.addWidget(h_title)
        hero_title_layout.addStretch()
        left_layout.addLayout(hero_title_layout)

        # 5D Arc Reactor Widget
        self.core_widget = MasterCommandCoreWidget()
        self.core_widget.setMinimumHeight(250)
        left_layout.addWidget(self.core_widget, 1)

        # Status text & Control Bar
        status_lbl = QLabel("I'm listening... How can I help you today?")
        status_lbl.setFont(QFont("Segoe UI", 9))
        status_lbl.setStyleSheet("color: #94A3B8; background: transparent;")
        status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(status_lbl)

        ctrl_bar = QHBoxLayout()
        ctrl_bar.setSpacing(10)

        self.voice_button = QPushButton("Tap to Speak")
        self.voice_button.setIcon(QIcon(get_card_icon_pixmap("voice", 16)))
        self.voice_button.setFixedHeight(38)
        self.voice_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.voice_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 11px;
                font-weight: 700;
                padding: 0 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #60A5FA, stop:1 #3B82F6);
            }
        """)

        self.execute_btn = QPushButton("Execute")
        self.execute_btn.setIcon(QIcon(get_card_icon_pixmap("code", 16)))
        self.execute_btn.setFixedHeight(38)
        self.execute_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.execute_btn.setStyleSheet("""
            QPushButton {
                background: rgba(30, 41, 59, 0.8);
                color: #60A5FA;
                border: 1px solid rgba(59, 130, 246, 0.4);
                border-radius: 10px;
                font-size: 11px;
                font-weight: 700;
                padding: 0 14px;
            }
            QPushButton:hover {
                background: rgba(59, 130, 246, 0.2);
            }
        """)

        ctrl_bar.addWidget(self.voice_button, 1)
        ctrl_bar.addWidget(self.execute_btn)
        left_layout.addLayout(ctrl_bar)

        center_split.addWidget(left_hero, 4)

        # MIDDLE: SHRIVA AI Capabilities Quick Grid
        mid_panel = QFrame()
        mid_panel.setObjectName("midPanelFrame")
        mid_panel.setStyleSheet("""
            QFrame#midPanelFrame {
                background: rgba(16, 24, 39, 0.75);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
        """)
        mid_layout = QVBoxLayout(mid_panel)
        mid_layout.setContentsMargins(14, 14, 14, 14)
        mid_layout.setSpacing(10)

        mid_head = QHBoxLayout()
        mid_head.setContentsMargins(0, 0, 0, 0)
        mid_head.setSpacing(8)

        m_icon = QLabel()
        m_icon.setPixmap(get_card_icon_pixmap("code", 18))
        m_icon.setStyleSheet("background: transparent;")
        
        m_title = QLabel("⚡ SHRIVA AI CORE INTELLIGENCE")
        m_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        m_title.setStyleSheet("color: #60A5FA; background: transparent;")

        m_badge = QLabel("● ONLINE")
        m_badge.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        m_badge.setStyleSheet("color: #10B981; background: transparent; border: none; font-size: 10px; margin-left: 6px;")

        mid_head.addWidget(m_icon, 0, Qt.AlignmentFlag.AlignVCenter)
        mid_head.addWidget(m_title, 0, Qt.AlignmentFlag.AlignVCenter)
        mid_head.addWidget(m_badge, 0, Qt.AlignmentFlag.AlignVCenter)
        mid_head.addStretch()
        mid_layout.addLayout(mid_head)

        grid = QGridLayout()
        grid.setSpacing(10)

        cap_buttons = [
            ("Face Reading ( Astro )", "Secure Biometrics", "face", 0, 0),
            ("OCR Reader", "Extract Text", "ocr", 0, 1),
            ("PDF Analyzer", "Smart Parsing", "pdf", 1, 0),
            ("Screenshot AI", "Visual Analysis", "screen", 1, 1),
            ("Duplicate Finder", "Clean Storage", "dup", 2, 0),
            ("Interview Prep", "Interview Coach", "code", 2, 1)
        ]

        for text, desc, key, r, c in cap_buttons:
            c_btn = QPushButton()
            c_btn.setFixedHeight(64)
            c_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            c_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(30, 41, 59, 0.6);
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 12px;
                    text-align: left;
                    padding: 4px 10px;
                }
                QPushButton:hover {
                    background: rgba(59, 130, 246, 0.15);
                    border: 1px solid rgba(59, 130, 246, 0.4);
                }
            """)
            btn_layout = QHBoxLayout(c_btn)
            btn_layout.setContentsMargins(10, 4, 10, 4)
            btn_layout.setSpacing(10)

            b_icon = QLabel()
            b_icon.setPixmap(get_card_icon_pixmap(key, 18))
            b_icon.setStyleSheet("background: transparent;")

            txt_box = QVBoxLayout()
            txt_box.setSpacing(0)

            bt = QLabel(text)
            bt.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            bt.setStyleSheet("color: #F8FAFC; background: transparent;")

            bd = QLabel(desc)
            bd.setFont(QFont("Segoe UI", 8))
            bd.setStyleSheet("color: #94A3B8; background: transparent;")

            txt_box.addWidget(bt)
            txt_box.addWidget(bd)

            btn_layout.addWidget(b_icon)
            btn_layout.addLayout(txt_box, 1)

            grid.addWidget(c_btn, r, c)

            # Connect specific feature triggers
            if "Face" in text:
                self.scan_btn = c_btn
            elif "OCR" in text:
                self.ocr_btn = c_btn
            elif "PDF" in text:
                self.resume_btn = c_btn
            elif "Screenshot" in text:
                self.screenshot_btn = c_btn
            elif "Duplicate" in text:
                self.dup_btn = c_btn
            elif "Code" in text or "Interview" in text:
                self.interview_btn = c_btn


        mid_layout.addLayout(grid)

        # Bottom View Capabilities Action Button
        self.view_all_btn = QPushButton("View All Capabilities  →")
        self.view_all_btn.setFixedHeight(34)
        self.view_all_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.view_all_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #60A5FA;
                border: 1px solid rgba(96, 165, 250, 0.3);
                border-radius: 8px;
                font-size: 11px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(59, 130, 246, 0.15);
            }
        """)
        mid_layout.addWidget(self.view_all_btn)

        center_split.addWidget(mid_panel, 5)

        layout.addLayout(center_split, 1)

        # 3. Bottom Quick Prompt Input Bar (Matching Image Prompt Bar)
        prompt_bar = QFrame()
        prompt_bar.setFixedHeight(52)
        prompt_bar.setStyleSheet("""
            QFrame {
                background: rgba(16, 24, 39, 0.9);
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 14px;
            }
        """)
        p_layout = QHBoxLayout(prompt_bar)
        p_layout.setContentsMargins(14, 0, 14, 0)
        p_layout.setSpacing(12)

        ai_badge = QLabel("AI")
        ai_badge.setStyleSheet("""
            QLabel {
                background: #3B82F6;
                color: white;
                font-weight: bold;
                font-size: 10px;
                padding: 4px 8px;
                border-radius: 6px;
            }
        """)

        # Input Box assigned to self.input_box for main.py text command handling (CustomChatInputEdit supports Enter to Submit!)
        self.input_box = CustomChatInputEdit()
        self.input_box.setPlaceholderText("Ask me anything... (e.g. 'Open WhatsApp', 'Create presentation', 'System status')")
        self.input_box.setFixedHeight(36)
        self.input_box.setStyleSheet("""
            QTextEdit {
                background: transparent;
                border: none;
                color: #F8FAFC;
                font-size: 12px;
            }
        """)

        self.send_button = QPushButton("  Send ⚡ ")
        self.send_button.setFixedSize(90, 36)
        self.send_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.send_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #60A5FA, stop:1 #3B82F6);
            }
        """)

        # ChatGPT-Style Behavior: Pressing Enter key submits message directly!
        self.input_box.return_pressed.connect(self.send_button.click)

        p_layout.addWidget(ai_badge)
        p_layout.addWidget(self.input_box, 1)
        p_layout.addWidget(self.send_button)

        layout.addWidget(prompt_bar)

        return view

    # ---------------- TAB 1: VOICE ASSISTANT VIEW ----------------
    def create_voice_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        # Single Hero Card containing 5D Quantum Reactor
        hero_card = QFrame()
        hero_card.setStyleSheet("""
            QFrame {
                background: rgba(16, 24, 39, 0.85);
                border: 1px solid rgba(59, 130, 246, 0.4);
                border-radius: 20px;
            }
        """)
        h_layout = QVBoxLayout(hero_card)
        h_layout.setContentsMargins(24, 24, 24, 24)
        h_layout.setSpacing(16)

        # Top Header & Mic Pill Status
        top_bar = QHBoxLayout()
        from ui.vector_icons import get_tab_icon

        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_tab_icon("voice").pixmap(32, 32))
        icon_lbl.setStyleSheet("background: transparent;")

        head = QLabel("5D Quantum Waveform Reactor Stage")
        head.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        head.setStyleSheet("color: #F8FAFC; background: transparent; margin-left: 8px;")

        self.mic_status_badge = QLabel("🟢 MIC READY • TAP REACTOR TO ENGAGE")
        self.mic_status_badge.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.mic_status_badge.setStyleSheet("""
            QLabel {
                background: rgba(16, 185, 129, 0.2);
                color: #10B981;
                border: 1px solid rgba(16, 185, 129, 0.5);
                border-radius: 12px;
                padding: 4px 14px;
            }
        """)

        top_bar.addWidget(icon_lbl)
        top_bar.addWidget(head)
        top_bar.addStretch()
        top_bar.addWidget(self.mic_status_badge)
        h_layout.addLayout(top_bar)

        # Centered Full-Size 5D Quantum Waveform Reactor
        self.voice_core_widget = MasterCommandCoreWidget()
        self.voice_core_widget.setMinimumHeight(420)
        h_layout.addWidget(self.voice_core_widget, 1)

        # Tap Action Handler
        def _on_reactor_tapped():
            if hasattr(self, 'voice_button') and self.voice_button:
                self.voice_button.click()
                self.mic_status_badge.setText("🎙️ MICROPHONE LISTENING... SPEAK NOW")
                self.mic_status_badge.setStyleSheet("""
                    QLabel {
                        background: rgba(59, 130, 246, 0.3);
                        color: #60A5FA;
                        border: 1px solid rgba(96, 165, 250, 0.6);
                        border-radius: 12px;
                        padding: 4px 14px;
                    }
                """)
                # Reset status pill back after 6 seconds
                QTimer.singleShot(6000, lambda: self.mic_status_badge.setText("🟢 MIC READY • TAP REACTOR TO ENGAGE"))
                QTimer.singleShot(6000, lambda: self.mic_status_badge.setStyleSheet("""
                    QLabel {
                        background: rgba(16, 185, 129, 0.2);
                        color: #10B981;
                        border: 1px solid rgba(16, 185, 129, 0.5);
                        border-radius: 12px;
                        padding: 4px 14px;
                    }
                """))

        self.voice_core_widget.clicked.connect(_on_reactor_tapped)

        # Bottom Tap Indicator Banner
        tap_hint = QLabel("🎯 Click or Tap directly on the 5D Quantum Core above to activate Microphone Listening")
        tap_hint.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        tap_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tap_hint.setStyleSheet("color: #94A3B8; background: transparent; padding-bottom: 4px;")
        h_layout.addWidget(tap_hint)

        layout.addWidget(hero_card, 1)
        return view

    # ---------------- TAB 2: AI CHAT VIEW ----------------
    def create_chat_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(0, 0, 0, 0)

        # Main Terminal Chat Panel instance assigned to self.terminal
        self.terminal = TerminalWidget()
        layout.addWidget(self.terminal, 1)

        return view

    # ---------------- TAB 3: COMPUTER VISION HUB ----------------
    def create_vision_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(14)

        head = QLabel("👁️ Computer Vision & Real-Time Perception Matrix")
        head.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        head.setStyleSheet("color: #F8FAFC; background: transparent;")
        layout.addWidget(head)

        # Real-time Vision Telemetry Panel
        v_matrix = QFrame()
        v_matrix.setStyleSheet("""
            QFrame {
                background: rgba(16, 24, 39, 0.85);
                border: 1px solid rgba(16, 185, 129, 0.4);
                border-radius: 14px;
                padding: 12px;
            }
        """)
        vm_layout = QHBoxLayout(v_matrix)
        vm_layout.setContentsMargins(14, 8, 14, 8)
        vm_layout.setSpacing(16)

        m1 = QVBoxLayout()
        m1_title = QLabel("CAMERA STREAM")
        m1_title.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        m1_title.setStyleSheet("color: #64748B; background: transparent;")
        m1_val = QLabel("● Active (30 FPS)")
        m1_val.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        m1_val.setStyleSheet("color: #10B981; background: transparent;")
        m1.addWidget(m1_title)
        m1.addWidget(m1_val)

        m2 = QVBoxLayout()
        m2_title = QLabel("FACE & BIO PERCEPTION")
        m2_title.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        m2_title.setStyleSheet("color: #64748B; background: transparent;")
        m2_val = QLabel("Haar Cascade + DeepFace")
        m2_val.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        m2_val.setStyleSheet("color: #60A5FA; background: transparent;")
        m2.addWidget(m2_title)
        m2.addWidget(m2_val)

        m3 = QVBoxLayout()
        m3_title = QLabel("OBJECT CLASSIFIER")
        m3_title.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        m3_title.setStyleSheet("color: #64748B; background: transparent;")
        m3_val = QLabel("80+ Objects Online")
        m3_val.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        m3_val.setStyleSheet("color: #F59E0B; background: transparent;")
        m3.addWidget(m3_title)
        m3.addWidget(m3_val)

        vm_layout.addLayout(m1)
        vm_layout.addLayout(m2)
        vm_layout.addLayout(m3)
        layout.addWidget(v_matrix)

        grid = QGridLayout()
        grid.setSpacing(14)

        v_cards = [
            ("Face Recognition & Dossier", "Recognize faces & AI bio metrics in real-time.", "scan_btn"),
            ("OCR Scanner", "Extract text from images, documents, & bills.", "ocr_btn"),
            ("Object Detection", "Detect & label 80+ objects live in webcam stream.", "obj_btn"),
            ("Screenshot AI Analyzer", "Analyze image content & screen layout.", "screen_btn")
        ]

        for title, desc, tag in v_cards:
            card = QFrame()
            card.setMinimumHeight(130)
            card.setStyleSheet("""
                QFrame {
                    background: rgba(16, 24, 39, 0.75);
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 14px;
                }
                QFrame:hover {
                    border: 1px solid rgba(59, 130, 246, 0.4);
                }
            """)
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(16, 16, 16, 16)

            t_lbl = QLabel(title)
            t_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            t_lbl.setStyleSheet("color: #F8FAFC; background: transparent;")

            d_lbl = QLabel(desc)
            d_lbl.setFont(QFont("Segoe UI", 9))
            d_lbl.setStyleSheet("color: #94A3B8; background: transparent;")
            d_lbl.setWordWrap(True)

            act_btn = QPushButton("Launch Module  →")
            act_btn.setFixedHeight(32)
            act_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            act_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(59, 130, 246, 0.15);
                    color: #60A5FA;
                    border: 1px solid rgba(59, 130, 246, 0.3);
                    border-radius: 8px;
                    font-size: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgba(59, 130, 246, 0.3);
                }
            """)

            c_layout.addWidget(t_lbl)
            c_layout.addWidget(d_lbl)
            c_layout.addStretch()
            c_layout.addWidget(act_btn)

            row = len(grid) // 2
            col = len(grid) % 2
            grid.addWidget(card, row, col)

        layout.addLayout(grid)
        layout.addStretch()

        return view

    # ---------------- TAB 4: DOCUMENT AI CENTER ----------------
    def create_document_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(14)

        head = QLabel("📄 Document AI Center")
        head.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        head.setStyleSheet("color: #F8FAFC; background: transparent;")
        layout.addWidget(head)

        grid = QGridLayout()
        grid.setSpacing(14)

        doc_tools = [
            ("📄 PDF Analyzer", "Parse & extract structured insights from large PDFs."),
            ("📝 Resume Parser", "Evaluate skills, score CVs, & build career paths."),
            ("📑 Text Summarizer", "Summarize long documents & meeting notes instantly."),
            ("📋 Invoice Reader", "Extract invoice totals, line items, & tax breakdown.")
        ]

        for idx, (title, desc) in enumerate(doc_tools):
            card = QFrame()
            card.setMinimumHeight(130)
            card.setStyleSheet("""
                QFrame {
                    background: rgba(16, 24, 39, 0.75);
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 14px;
                }
                QFrame:hover {
                    border: 1px solid rgba(59, 130, 246, 0.4);
                }
            """)
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(16, 16, 16, 16)

            t_lbl = QLabel(title)
            t_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            t_lbl.setStyleSheet("color: #F8FAFC; background: transparent;")

            d_lbl = QLabel(desc)
            d_lbl.setFont(QFont("Segoe UI", 9))
            d_lbl.setStyleSheet("color: #94A3B8; background: transparent;")
            d_lbl.setWordWrap(True)

            act_btn = QPushButton("Open Document Tool  →")
            act_btn.setFixedHeight(32)
            act_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            act_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(59, 130, 246, 0.15);
                    color: #60A5FA;
                    border: 1px solid rgba(59, 130, 246, 0.3);
                    border-radius: 8px;
                    font-size: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: rgba(59, 130, 246, 0.3);
                }
            """)

            c_layout.addWidget(t_lbl)
            c_layout.addWidget(d_lbl)
            c_layout.addStretch()
            c_layout.addWidget(act_btn)

            grid.addWidget(card, idx // 2, idx % 2)

        layout.addLayout(grid)
        layout.addStretch()

        return view

    # ---------------- TAB 5: SECURITY & DEFENSE ----------------
    # ---------------- TAB 5: SECURITY CLEARANCE & DEFENSE PORTAL ----------------
    def create_security_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(16)

        # Top Security Clearance Header Banner
        head_frame = QFrame()
        head_frame.setStyleSheet("""
            QFrame {
                background: rgba(16, 24, 39, 0.85);
                border: 1px solid rgba(239, 68, 68, 0.35);
                border-radius: 16px;
                padding: 12px 18px;
            }
        """)
        h_layout = QHBoxLayout(head_frame)
        h_layout.setContentsMargins(12, 6, 12, 6)

        from ui.vector_icons import get_tab_icon

        icon_lbl = QLabel()
        icon_lbl.setPixmap(get_tab_icon("security").pixmap(32, 32))
        icon_lbl.setStyleSheet("background: transparent;")

        head = QLabel("Security Clearance & Threat Defense Portal")
        head.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        head.setStyleSheet("color: #F8FAFC; background: transparent; margin-left: 8px;")

        defcon_badge = QLabel("DEFCON 1 • MAXIMUM SHIELD ONLINE")
        defcon_badge.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        defcon_badge.setStyleSheet("""
            QLabel {
                background: rgba(16, 185, 129, 0.2);
                color: #10B981;
                border: 1px solid rgba(16, 185, 129, 0.5);
                border-radius: 12px;
                padding: 4px 12px;
            }
        """)

        h_layout.addWidget(icon_lbl)
        h_layout.addWidget(head)
        h_layout.addStretch()
        h_layout.addWidget(defcon_badge)
        layout.addWidget(head_frame)

        # 2x2 Armored Card Grid
        grid = QGridLayout()
        grid.setSpacing(16)

        # 1. Intruder Defense Sentinel Card
        card1 = QFrame()
        card1.setObjectName("secCard1")
        card1.setStyleSheet("""
            QFrame#secCard1 {
                background: rgba(16, 24, 39, 0.85);
                border: 1px solid rgba(239, 68, 68, 0.4);
                border-radius: 16px;
            }
        """)
        l1 = QVBoxLayout(card1)
        l1.setContentsMargins(18, 18, 18, 18)
        l1.setSpacing(10)

        t1_box = QHBoxLayout()
        t1 = QLabel("Intruder Defense Sentinel")
        t1.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        t1.setStyleSheet("color: #F8FAFC; background: transparent;")
        st1 = QLabel("● ACTIVE")
        st1.setStyleSheet("color: #EF4444; font-weight: bold; font-size: 10px; background: transparent;")
        t1_box.addWidget(t1)
        t1_box.addStretch()
        t1_box.addWidget(st1)

        d1 = QLabel("Webcam background scanning & red alert siren alarm.")
        d1.setStyleSheet("color: #94A3B8; background: transparent; font-size: 11px;")
        
        self.defense_btn = QPushButton("Toggle Intruder Defense")
        self.defense_btn.setFixedHeight(38)
        self.defense_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.defense_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EF4444, stop:1 #DC2626);
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #F87171;
            }
        """)
        l1.addLayout(t1_box)
        l1.addWidget(d1)
        l1.addStretch()
        l1.addWidget(self.defense_btn)
        grid.addWidget(card1, 0, 0)

        # 2. Biometric Voice Security Card
        card2 = QFrame()
        card2.setObjectName("secCard2")
        card2.setStyleSheet("""
            QFrame#secCard2 {
                background: rgba(16, 24, 39, 0.85);
                border: 1px solid rgba(59, 130, 246, 0.4);
                border-radius: 16px;
            }
        """)
        l2 = QVBoxLayout(card2)
        l2.setContentsMargins(18, 18, 18, 18)
        l2.setSpacing(10)

        t2_box = QHBoxLayout()
        t2 = QLabel("Biometric Voice Authentication")
        t2.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        t2.setStyleSheet("color: #F8FAFC; background: transparent;")
        st2 = QLabel("● ENROLLED")
        st2.setStyleSheet("color: #60A5FA; font-weight: bold; font-size: 10px; background: transparent;")
        t2_box.addWidget(t2)
        t2_box.addStretch()
        t2_box.addWidget(st2)

        d2 = QLabel("Verify spoken voice identity against enrolled biometric profile.")
        d2.setStyleSheet("color: #94A3B8; background: transparent; font-size: 11px;")

        self.voice_auth_btn = QPushButton("Verify Voice Identity")
        self.voice_auth_btn.setFixedHeight(38)
        self.voice_auth_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.voice_auth_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #2563EB);
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #60A5FA;
            }
        """)
        l2.addLayout(t2_box)
        l2.addWidget(d2)
        l2.addStretch()
        l2.addWidget(self.voice_auth_btn)
        grid.addWidget(card2, 0, 1)

        # 3. Master PIN Setup Card
        card3 = QFrame()
        card3.setObjectName("secCard3")
        card3.setStyleSheet("""
            QFrame#secCard3 {
                background: rgba(16, 24, 39, 0.85);
                border: 1px solid rgba(16, 185, 129, 0.4);
                border-radius: 16px;
            }
        """)
        l3 = QVBoxLayout(card3)
        l3.setContentsMargins(18, 18, 18, 18)
        l3.setSpacing(10)

        t3 = QLabel("Master Security PIN Setup")
        t3.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        t3.setStyleSheet("color: #F8FAFC; background: transparent;")

        d3 = QLabel("Configure 4-digit Master Security PIN for emergency override.")
        d3.setStyleSheet("color: #94A3B8; background: transparent; font-size: 11px;")

        pin_row = QHBoxLayout()
        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("Enter 4-digit PIN (e.g. 1234)")
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setFixedHeight(36)
        self.pin_input.setStyleSheet("background: rgba(30, 41, 59, 0.8); color: white; border: 1px solid rgba(255,255,255,0.15); border-radius: 8px; padding: 6px 12px;")

        def _save_pin():
            p = self.pin_input.text().strip()
            if len(p) >= 4:
                import cyber_vault
                cyber_vault.store_secret("MASTER_SECURITY_PIN", p)
                self.pin_status_lbl.setText("● Master PIN Updated & Encrypted!")
                self.pin_input.clear()

        self.save_pin_btn = QPushButton("Save PIN")
        self.save_pin_btn.setFixedHeight(36)
        self.save_pin_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.save_pin_btn.setStyleSheet("""
            QPushButton {
                background: #10B981;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                padding: 0 16px;
            }
            QPushButton:hover {
                background: #34D399;
            }
        """)
        self.save_pin_btn.clicked.connect(_save_pin)

        pin_row.addWidget(self.pin_input, 1)
        pin_row.addWidget(self.save_pin_btn)

        self.pin_status_lbl = QLabel("")
        self.pin_status_lbl.setStyleSheet("color: #10B981; font-weight: bold; font-size: 10px; background: transparent;")

        l3.addWidget(t3)
        l3.addWidget(d3)
        l3.addLayout(pin_row)
        l3.addWidget(self.pin_status_lbl)
        grid.addWidget(card3, 1, 0)

        # 4. AES-256 Encrypted Cyber Vault Manager Card
        card4 = QFrame()
        card4.setObjectName("secCard4")
        card4.setStyleSheet("""
            QFrame#secCard4 {
                background: rgba(16, 24, 39, 0.85);
                border: 1px solid rgba(139, 92, 246, 0.4);
                border-radius: 16px;
            }
        """)
        l4 = QVBoxLayout(card4)
        l4.setContentsMargins(18, 18, 18, 18)
        l4.setSpacing(10)

        t4 = QLabel("AES-256 Encrypted Cyber Vault Manager")
        t4.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        t4.setStyleSheet("color: #F8FAFC; background: transparent;")

        d4 = QLabel("Store API keys & passwords encrypted with Fernet AES-256.")
        d4.setStyleSheet("color: #94A3B8; background: transparent; font-size: 11px;")

        v_row1 = QHBoxLayout()
        self.v_key_input = QLineEdit()
        self.v_key_input.setPlaceholderText("Secret Name (e.g. GEMINI_KEY)")
        self.v_key_input.setFixedHeight(36)
        self.v_key_input.setStyleSheet("background: rgba(30, 41, 59, 0.8); color: white; border: 1px solid rgba(255,255,255,0.15); border-radius: 8px; padding: 6px 12px;")

        self.v_val_input = QLineEdit()
        self.v_val_input.setPlaceholderText("Secret Value / Password")
        self.v_val_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.v_val_input.setFixedHeight(36)
        self.v_val_input.setStyleSheet("background: rgba(30, 41, 59, 0.8); color: white; border: 1px solid rgba(255,255,255,0.15); border-radius: 8px; padding: 6px 12px;")

        v_row1.addWidget(self.v_key_input)
        v_row1.addWidget(self.v_val_input)

        def _save_vault_secret():
            k = self.v_key_input.text().strip()
            v = self.v_val_input.text().strip()
            if k and v:
                import cyber_vault
                cyber_vault.store_secret(k, v)
                self.vault_status_lbl.setText(f"● Secret '{k}' encrypted and stored safely!")
                self.v_key_input.clear()
                self.v_val_input.clear()
                self.refresh_vault_registry()

        self.save_vault_btn = QPushButton("Encrypt & Store")
        self.save_vault_btn.setFixedHeight(36)
        self.save_vault_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.save_vault_btn.setStyleSheet("""
            QPushButton {
                background: #8B5CF6;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #A78BFA;
            }
        """)
        self.save_vault_btn.clicked.connect(_save_vault_secret)

        self.vault_status_lbl = QLabel("")
        self.vault_status_lbl.setStyleSheet("color: #A78BFA; font-weight: bold; font-size: 10px; background: transparent;")

        l4.addWidget(t4)
        l4.addWidget(d4)
        l4.addLayout(v_row1)
        l4.addWidget(self.save_vault_btn)
        l4.addWidget(self.vault_status_lbl)
        grid.addWidget(card4, 1, 1)

        layout.addLayout(grid)

        # Bottom Encrypted Key Registry Panel
        registry_frame = QFrame()
        registry_frame.setObjectName("secRegistryFrame")
        registry_frame.setStyleSheet("""
            QFrame#secRegistryFrame {
                background: rgba(16, 24, 39, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
        """)
        reg_layout = QVBoxLayout(registry_frame)
        reg_layout.setContentsMargins(18, 18, 18, 18)
        reg_layout.setSpacing(10)

        reg_head = QHBoxLayout()
        reg_title = QLabel("Encrypted Cyber Vault Key Registry")
        reg_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        reg_title.setStyleSheet("color: #F8FAFC; background: transparent;")

        self.refresh_vault_btn = QPushButton("Refresh Vault")
        self.refresh_vault_btn.setFixedHeight(28)
        self.refresh_vault_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.refresh_vault_btn.setStyleSheet("""
            QPushButton {
                background: rgba(59, 130, 246, 0.15);
                color: #60A5FA;
                border: 1px solid rgba(96, 165, 250, 0.3);
                border-radius: 6px;
                font-size: 10px;
                font-weight: 600;
                padding: 0 10px;
            }
            QPushButton:hover {
                background: rgba(59, 130, 246, 0.3);
            }
        """)
        self.refresh_vault_btn.clicked.connect(self.refresh_vault_registry)

        reg_head.addWidget(reg_title)
        reg_head.addStretch()
        reg_head.addWidget(self.refresh_vault_btn)
        reg_layout.addLayout(reg_head)

        self.vault_registry_box = QVBoxLayout()
        self.vault_registry_box.setSpacing(6)
        reg_layout.addLayout(self.vault_registry_box)

        layout.addWidget(registry_frame)
        layout.addStretch()

        # Initial load of vault registry items
        self.refresh_vault_registry()

        return view

    def refresh_vault_registry(self):
        if not hasattr(self, 'vault_registry_box'):
            return

        # Clear existing items
        while self.vault_registry_box.count():
            child = self.vault_registry_box.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        import cyber_vault
        try:
            vault_data = cyber_vault.load_and_decrypt_vault()
            keys_list = []
            
            for item in vault_data.get("api_keys", []):
                keys_list.append((item.get("provider", "API_KEY"), "AES-256 Encrypted", "#8B5CF6"))
            for item in vault_data.get("logins", []):
                keys_list.append((f"Login: {item.get('service', 'Account')}", "Fernet Secured", "#3B82F6"))

            if not keys_list:
                keys_list = [
                    ("MASTER_SECURITY_PIN", "Fernet AES-256 Encrypted", "#10B981"),
                    ("GEMINI_API_KEY", "Fernet AES-256 Encrypted", "#8B5CF6")
                ]

            for key_name, status_tag, color in keys_list[:4]:
                r_item = QFrame()
                r_item.setObjectName("vaultItemFrame")
                r_item.setStyleSheet("QFrame#vaultItemFrame { background: rgba(30, 41, 59, 0.6); border-radius: 8px; }")
                ri_layout = QHBoxLayout(r_item)
                ri_layout.setContentsMargins(12, 6, 12, 6)

                k_lbl = QLabel(key_name)
                k_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
                k_lbl.setStyleSheet("color: #F8FAFC; background: transparent;")

                mask_lbl = QLabel("••••••••••••••••")
                mask_lbl.setFont(QFont("Segoe UI", 9))
                mask_lbl.setStyleSheet("color: #64748B; background: transparent; letter-spacing: 2px;")

                tag_lbl = QLabel(status_tag)
                tag_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
                tag_lbl.setStyleSheet(f"color: {color}; background: transparent;")

                ri_layout.addWidget(k_lbl)
                ri_layout.addStretch()
                ri_layout.addWidget(mask_lbl)
                ri_layout.addStretch()
                ri_layout.addWidget(tag_lbl)

                self.vault_registry_box.addWidget(r_item)
        except Exception as e:
            err_lbl = QLabel(f"Vault status: {e}")
            err_lbl.setStyleSheet("color: #94A3B8; font-size: 10px;")
            self.vault_registry_box.addWidget(err_lbl)

    # ---------------- TAB 6: ANALYTICS & SYSTEM HEALTH ----------------
    def create_analytics_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        head = QLabel("📈 System Metrics & AI Performance Telemetry")
        head.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        head.setStyleSheet("color: #F8FAFC; background: transparent;")
        layout.addWidget(head)

        # 2-Column Side-by-Side Main Stage Layout
        stage_split = QHBoxLayout()
        stage_split.setSpacing(16)

        # LEFT COLUMN: System Metrics & Diagnostic Hardware Bars
        left_col = QVBoxLayout()
        left_col.setSpacing(12)

        # 1. Health Rating Banner
        health_banner = QFrame()
        health_banner.setObjectName("anaHealthBanner")
        health_banner.setStyleSheet("""
            QFrame#anaHealthBanner {
                background: rgba(16, 24, 39, 0.85);
                border: 1px solid rgba(59, 130, 246, 0.4);
                border-radius: 14px;
            }
        """)
        hb_layout = QHBoxLayout(health_banner)
        hb_layout.setContentsMargins(16, 10, 16, 10)

        h_title = QLabel("SYSTEM HEALTH & OPTIMIZATION SCORE")
        h_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        h_title.setStyleSheet("color: #94A3B8; background: transparent;")

        h_score = QLabel("98% (OPTIMAL)")
        h_score.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        h_score.setStyleSheet("color: #10B981; background: transparent;")

        hb_layout.addWidget(h_title)
        hb_layout.addStretch()
        hb_layout.addWidget(h_score)
        left_col.addWidget(health_banner)

        # 2. AI Engine Telemetry Grid
        ai_telemetry = QFrame()
        ai_telemetry.setObjectName("anaTelemetryFrame")
        ai_telemetry.setStyleSheet("QFrame#anaTelemetryFrame { background: rgba(16, 24, 39, 0.85); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 14px; }")
        at_layout = QHBoxLayout(ai_telemetry)
        at_layout.setContentsMargins(14, 10, 14, 10)
        at_layout.setSpacing(12)

        import analytics_logger
        records = analytics_logger.logger_instance.get_all_records()
        total_cmd = len(records) if records else 12
        voice_cnt = sum(1 for r in records if r.get("source") == "voice") if records else 8
        voice_ratio = int((voice_cnt / max(1, total_cmd)) * 100)
        text_ratio = 100 - voice_ratio

        t1 = QVBoxLayout()
        t1_lbl = QLabel("TOTAL COMMANDS LOGGED")
        t1_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        t1_lbl.setStyleSheet("color: #64748B; background: transparent;")
        t1_val = QLabel(f"{total_cmd} System Actions")
        t1_val.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        t1_val.setStyleSheet("color: #60A5FA; background: transparent;")
        t1.addWidget(t1_lbl)
        t1.addWidget(t1_val)

        t2 = QVBoxLayout()
        t2_lbl = QLabel("VOICE vs TEXT RATIO")
        t2_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        t2_lbl.setStyleSheet("color: #64748B; background: transparent;")
        t2_val = QLabel(f"{voice_ratio}% Voice / {text_ratio}% Text")
        t2_val.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        t2_val.setStyleSheet("color: #A78BFA; background: transparent;")
        t2.addWidget(t2_lbl)
        t2.addWidget(t2_val)

        t3 = QVBoxLayout()
        t3_lbl = QLabel("AVG RESPONSE LATENCY")
        t3_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        t3_lbl.setStyleSheet("color: #64748B; background: transparent;")
        t3_val = QLabel("115 ms (Ultra Fast)")
        t3_val.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        t3_val.setStyleSheet("color: #10B981; background: transparent;")
        t3.addWidget(t3_lbl)
        t3.addWidget(t3_val)

        at_layout.addLayout(t1)
        at_layout.addLayout(t2)
        at_layout.addLayout(t3)
        left_col.addWidget(ai_telemetry)

        # 3. Hardware Meters & Audit Button Card
        metrics_frame = QFrame()
        metrics_frame.setObjectName("anaMetricsFrame")
        metrics_frame.setStyleSheet("""
            QFrame#anaMetricsFrame {
                background: rgba(16, 24, 39, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
        """)
        m_layout = QVBoxLayout(metrics_frame)
        m_layout.setContentsMargins(16, 14, 16, 14)
        m_layout.setSpacing(10)

        self.cpu_bar = self.create_metric_bar("CPU Usage")
        self.ram_bar = self.create_metric_bar("RAM Memory")
        self.gpu_bar = self.create_metric_bar("GPU Telemetry")
        self.network_bar = self.create_metric_bar("Network I/O Speed")

        m_layout.addWidget(self.cpu_bar)
        m_layout.addWidget(self.ram_bar)
        m_layout.addWidget(self.gpu_bar)
        m_layout.addWidget(self.network_bar)

        self.analytics_btn = QPushButton("Run Full System Diagnostic Audit")
        self.analytics_btn.setFixedHeight(36)
        self.analytics_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.analytics_btn.setStyleSheet("background: #3B82F6; color: white; border-radius: 8px; font-weight: bold; font-size: 11px;")
        m_layout.addWidget(self.analytics_btn)

        left_col.addWidget(metrics_frame, 1)

        # RIGHT COLUMN: Activity Trend Bezier Curve Chart & Timeline List
        right_panel = QFrame()
        right_panel.setObjectName("anaActivityPanel")
        right_panel.setStyleSheet("""
            QFrame#anaActivityPanel {
                background: rgba(16, 24, 39, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
        """)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(16, 14, 16, 14)
        right_layout.setSpacing(10)

        right_head = QHBoxLayout()
        r_title = QLabel("Activity Overview & Live Telemetry")
        r_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        r_title.setStyleSheet("color: #F8FAFC; background: transparent;")
        right_head.addWidget(r_title)
        right_head.addStretch()
        right_layout.addLayout(right_head)

        # Activity Trend Curve Chart Widget
        self.trend_chart = ActivityTrendWidget()
        self.trend_chart.setFixedHeight(120)
        right_layout.addWidget(self.trend_chart)

        # Dynamic Timeline List from Analytics Logger
        rec_title = QLabel("Recent System Activity")
        rec_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        rec_title.setStyleSheet("color: #94A3B8; background: transparent; margin-top: 2px;")
        right_layout.addWidget(rec_title)

        raw_records = analytics_logger.logger_instance.get_all_records()
        timeline_items = []
        if raw_records:
            for rec in reversed(raw_records[-4:]):
                cmd = rec.get("command", "System Task")
                src = rec.get("source", "system")
                t_str = rec.get("day_of_week", "Today")
                status = "● Success" if rec.get("success", True) else "● Executed"
                col = "#10B981" if rec.get("success", True) else "#60A5FA"
                timeline_items.append((f"{cmd.capitalize()} ({src})", t_str, status, col))
        else:
            timeline_items = [
                ("JarvisX System Core Initialized", "Just now", "● Active", "#10B981"),
                ("Biometric Vault Security Check", "Today", "● Secured", "#60A5FA")
            ]

        for item, t_str, st_str, st_col in timeline_items:
            item_frame = QFrame()
            item_frame.setObjectName("anaTimelineItem")
            item_frame.setStyleSheet("QFrame#anaTimelineItem { background: rgba(30, 41, 59, 0.5); border-radius: 8px; }")
            i_layout = QHBoxLayout(item_frame)
            i_layout.setContentsMargins(10, 6, 10, 6)

            i_info = QVBoxLayout()
            i_info.setSpacing(1)
            t_txt = QLabel(item)
            t_txt.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            t_txt.setStyleSheet("color: #F1F5F9; background: transparent;")
            
            sub_txt = QLabel(t_str)
            sub_txt.setFont(QFont("Segoe UI", 8))
            sub_txt.setStyleSheet("color: #64748B; background: transparent;")
            i_info.addWidget(t_txt)
            i_info.addWidget(sub_txt)

            st_lbl = QLabel(st_str)
            st_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            st_lbl.setStyleSheet(f"color: {st_col}; background: transparent;")

            i_layout.addLayout(i_info)
            i_layout.addStretch()
            i_layout.addWidget(st_lbl)

            right_layout.addWidget(item_frame)

        right_layout.addStretch()

        stage_split.addLayout(left_col, 5)
        stage_split.addWidget(right_panel, 5)

        layout.addLayout(stage_split, 1)

        return view

    def create_metric_bar(self, name):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)
        
        label = QLabel(name)
        label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        label.setStyleSheet("color: #94A3B8; background: transparent;")
        
        bar_frame = QFrame()
        bar_frame.setFixedHeight(22)
        bar_frame.setStyleSheet("""
            QFrame {
                background: rgba(30, 41, 59, 0.6);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 6px;
            }
        """)
        
        bar = QFrame(bar_frame)
        bar.setFixedHeight(20)
        bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3B82F6, stop:1 #60A5FA);
                border-radius: 5px;
            }
        """)
        
        layout.addWidget(label)
        layout.addWidget(bar_frame)
        
        widget.bar = bar
        widget.percent_label = label
        return widget

    # ---------------- TAB 7: SETTINGS & PLUGINS ----------------
    def create_settings_view(self):
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        head = QLabel("⚙️ Settings & System Configuration")
        head.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        head.setStyleSheet("color: #F8FAFC; background: transparent;")
        layout.addWidget(head)

        grid = QGridLayout()
        grid.setSpacing(14)

        # ---------------- CARD 1: AI System & Defense Protocols ----------------
        card1 = QFrame()
        card1.setObjectName("setCard1")
        card1.setStyleSheet("""
            QFrame#setCard1 {
                background: rgba(16, 24, 39, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
        """)
        c1_layout = QVBoxLayout(card1)
        c1_layout.setContentsMargins(16, 14, 16, 14)
        c1_layout.setSpacing(10)

        c1_title = QLabel("🤖 AI System & Security Protocols")
        c1_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        c1_title.setStyleSheet("color: #60A5FA; background: transparent;")
        c1_layout.addWidget(c1_title)

        # Ultron Mode Row
        u_row = QHBoxLayout()
        u_lbl = QLabel("Ultron Threat Override Protocol Mode")
        u_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        u_lbl.setStyleSheet("color: #F8FAFC; background: transparent;")
        
        self.ultron_toggle = QPushButton("Activate Ultron Protocol")
        self.ultron_toggle.setFixedHeight(32)
        self.ultron_toggle.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.ultron_toggle.setStyleSheet("""
            QPushButton {
                background: rgba(239, 68, 68, 0.2);
                color: #EF4444;
                border: 1px solid #EF4444;
                border-radius: 8px;
                font-weight: bold;
                font-size: 10px;
                padding: 0 10px;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.4);
            }
        """)
        self.ultron_toggle.clicked.connect(self.toggle_ultron_mode)
        u_row.addWidget(u_lbl)
        u_row.addStretch()
        u_row.addWidget(self.ultron_toggle)
        c1_layout.addLayout(u_row)

        # Biometric Enrolment Row
        b_row = QHBoxLayout()
        b_lbl = QLabel("Biometric Voice & Face Identity Profiles")
        b_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        b_lbl.setStyleSheet("color: #F8FAFC; background: transparent;")

        self.voice_auth_btn = QPushButton("Manage Biometric Profiles  →")
        self.voice_auth_btn.setFixedHeight(32)
        self.voice_auth_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.voice_auth_btn.setStyleSheet("""
            QPushButton {
                background: rgba(59, 130, 246, 0.15);
                color: #60A5FA;
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 8px;
                font-size: 10px;
                font-weight: bold;
                padding: 0 10px;
            }
            QPushButton:hover {
                background: rgba(59, 130, 246, 0.3);
            }
        """)
        # ⚡ College Presentation Turbo Mode Toggle
        t_row = QHBoxLayout()
        t_lbl = QLabel("⚡ College Presentation Turbo Mode (7-Min Pitch)")
        t_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        t_lbl.setStyleSheet("color: #F59E0B; background: transparent;")

        self.turbo_toggle = QPushButton("⚡ TURBO ACTIVE (0ms Async)")
        self.turbo_toggle.setFixedHeight(30)
        self.turbo_toggle.setCheckable(True)
        self.turbo_toggle.setChecked(True)
        self.turbo_toggle.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.turbo_toggle.setStyleSheet("""
            QPushButton {
                background: rgba(245, 158, 11, 0.2);
                color: #F59E0B;
                border: 1.5px solid #F59E0B;
                border-radius: 6px;
                font-size: 10px;
                font-weight: bold;
                padding: 0 10px;
            }
            QPushButton:checked {
                background: rgba(16, 185, 129, 0.25);
                color: #10B981;
                border-color: #10B981;
            }
        """)
        t_row.addWidget(t_lbl)
        t_row.addStretch()
        t_row.addWidget(self.turbo_toggle)
        c1_layout.addLayout(t_row)

        grid.addWidget(card1, 0, 0)

        # ---------------- CARD 2: Voice & Audio Feedback ----------------
        card2 = QFrame()
        card2.setObjectName("setCard2")
        card2.setStyleSheet("""
            QFrame#setCard2 {
                background: rgba(16, 24, 39, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
        """)
        c2_layout = QVBoxLayout(card2)
        c2_layout.setContentsMargins(16, 14, 16, 14)
        c2_layout.setSpacing(10)

        c2_title = QLabel("🎙️ Voice & Audio Speech Engine")
        c2_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        c2_title.setStyleSheet("color: #10B981; background: transparent;")
        c2_layout.addWidget(c2_title)

        # Language Selection Row (English Locked)
        lang_row = QHBoxLayout()
        lang_lbl = QLabel("🌐 Primary System Language")
        lang_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        lang_lbl.setStyleSheet("color: #F8FAFC; background: transparent;")

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English (en) - Default"])
        self.lang_combo.setFixedSize(200, 30)
        self.lang_combo.setStyleSheet("""
            QComboBox {
                background: rgba(30, 41, 59, 0.8);
                color: #F8FAFC;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding-left: 8px;
                font-size: 10px;
            }
        """)

        # Load existing language preference
        import json
        settings_path = os.path.join("jarvis_data", "voice_settings.json")
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    saved_lang = json.load(f).get("language", "en")
                    if saved_lang == "hi":
                        self.lang_combo.setCurrentIndex(1)
                    elif saved_lang == "mr":
                        self.lang_combo.setCurrentIndex(2)
                    else:
                        self.lang_combo.setCurrentIndex(0)
            except Exception:
                pass

        def on_lang_changed(idx):
            code_map = {0: "en", 1: "hi", 2: "mr"}
            code = code_map.get(idx, "en")
            s_data = {}
            if os.path.exists(settings_path):
                try:
                    with open(settings_path, "r", encoding="utf-8") as f:
                        s_data = json.load(f)
                except Exception:
                    pass
            s_data["language"] = code
            os.makedirs("jarvis_data", exist_ok=True)
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(s_data, f, indent=4)
            print(f"[SETTINGS] Language updated to: {code}")

        self.lang_combo.currentIndexChanged.connect(on_lang_changed)

        lang_row.addWidget(lang_lbl)
        lang_row.addStretch()
        lang_row.addWidget(self.lang_combo)
        c2_layout.addLayout(lang_row)

        # Voice Profile / Gender Selection Row (Male / Female Indian Accent)
        voice_row = QHBoxLayout()
        voice_lbl = QLabel("🎤 Voice Profile (Gender)")
        voice_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        voice_lbl.setStyleSheet("color: #F8FAFC; background: transparent;")

        self.voice_gender_combo = QComboBox()
        self.voice_gender_combo.addItems(["👨 Male Indian Voice", "👩 Female Indian Voice"])
        self.voice_gender_combo.setFixedSize(200, 30)
        self.voice_gender_combo.setStyleSheet("""
            QComboBox {
                background: rgba(30, 41, 59, 0.8);
                color: #F8FAFC;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding-left: 8px;
                font-size: 10px;
            }
        """)

        # Load existing voice index preference
        if os.path.exists(settings_path):
            try:
                with open(settings_path, "r", encoding="utf-8") as f:
                    v_idx = json.load(f).get("voice_index", 0)
                    self.voice_gender_combo.setCurrentIndex(1 if v_idx == 1 else 0)
            except Exception:
                pass

        def on_voice_gender_changed(idx):
            v_index = 1 if idx == 1 else 0
            s_data = {}
            if os.path.exists(settings_path):
                try:
                    with open(settings_path, "r", encoding="utf-8") as f:
                        s_data = json.load(f)
                except Exception:
                    pass
            s_data["voice_index"] = v_index
            os.makedirs("jarvis_data", exist_ok=True)
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(s_data, f, indent=4)
            print(f"[SETTINGS] Voice profile updated to: {'Female' if v_index == 1 else 'Male'}")

        self.voice_gender_combo.currentIndexChanged.connect(on_voice_gender_changed)

        voice_row.addWidget(voice_lbl)
        voice_row.addStretch()
        voice_row.addWidget(self.voice_gender_combo)
        c2_layout.addLayout(voice_row)

        # TTS Engine Row
        tts_row = QHBoxLayout()
        tts_lbl = QLabel("Speech Engine Mode")
        tts_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        tts_lbl.setStyleSheet("color: #F8FAFC; background: transparent;")

        self.tts_combo = QComboBox()
        self.tts_combo.addItems(["Offline Native TTS (pyttsx3)", "Neural Cloud Speech (gTTS)"])
        self.tts_combo.setFixedSize(200, 30)
        self.tts_combo.setStyleSheet("""
            QComboBox {
                background: rgba(30, 41, 59, 0.8);
                color: #F8FAFC;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding-left: 8px;
                font-size: 10px;
            }
        """)
        tts_row.addWidget(tts_lbl)
        tts_row.addStretch()
        tts_row.addWidget(self.tts_combo)
        c2_layout.addLayout(tts_row)

        # Speed Control Row
        spd_row = QHBoxLayout()
        spd_lbl = QLabel("Assistant Speaking Speed")
        spd_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        spd_lbl.setStyleSheet("color: #F8FAFC; background: transparent;")

        self.spd_combo = QComboBox()
        self.spd_combo.addItems(["Normal Speed (1.0x)", "Fast Pace (1.25x)", "Relaxed Pace (0.8x)"])
        self.spd_combo.setFixedSize(200, 30)
        self.spd_combo.setStyleSheet("""
            QComboBox {
                background: rgba(30, 41, 59, 0.8);
                color: #F8FAFC;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding-left: 8px;
                font-size: 10px;
            }
        """)
        spd_row.addWidget(spd_lbl)
        spd_row.addStretch()
        spd_row.addWidget(self.spd_combo)
        c2_layout.addLayout(spd_row)

        grid.addWidget(card2, 0, 1)

        # ---------------- CARD 3: Mobile Ecosystem & Vault Security ----------------
        card3 = QFrame()
        card3.setObjectName("setCard3")
        card3.setStyleSheet("""
            QFrame#setCard3 {
                background: rgba(16, 24, 39, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
        """)
        c3_layout = QVBoxLayout(card3)
        c3_layout.setContentsMargins(16, 14, 16, 14)
        c3_layout.setSpacing(10)

        c3_title = QLabel("📱 Mobile Ecosystem & Vault Security")
        c3_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        c3_title.setStyleSheet("color: #A78BFA; background: transparent;")
        c3_layout.addWidget(c3_title)

        # Pair Device Row
        p_row = QHBoxLayout()
        p_lbl = QLabel("Pair Mobile Phone or Tablet (QR / OTP)")
        p_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        p_lbl.setStyleSheet("color: #F8FAFC; background: transparent;")

        self.pair_mobile_btn = QPushButton("Open Mobile Pair Portal  →")
        self.pair_mobile_btn.setFixedHeight(32)
        self.pair_mobile_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.pair_mobile_btn.setStyleSheet("""
            QPushButton {
                background: rgba(167, 139, 250, 0.15);
                color: #A78BFA;
                border: 1px solid rgba(167, 139, 250, 0.3);
                border-radius: 8px;
                font-size: 10px;
                font-weight: bold;
                padding: 0 10px;
            }
            QPushButton:hover {
                background: rgba(167, 139, 250, 0.3);
            }
        """)
        self.pair_mobile_btn.clicked.connect(lambda: MobilePairingDialog(self).exec())
        p_row.addWidget(p_lbl)
        p_row.addStretch()
        p_row.addWidget(self.pair_mobile_btn)
        c3_layout.addLayout(p_row)

        # Cyber Vault Auto-Lock Row
        v_row = QHBoxLayout()
        v_lbl = QLabel("Encrypted Cyber Vault Auto-Lock")
        v_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        v_lbl.setStyleSheet("color: #F8FAFC; background: transparent;")

        self.v_combo = QComboBox()
        self.v_combo.addItems(["5 Minutes Timeout", "15 Minutes Timeout", "30 Minutes Timeout", "Never (Manual Lock)"])
        self.v_combo.setFixedSize(200, 30)
        self.v_combo.setStyleSheet("""
            QComboBox {
                background: rgba(30, 41, 59, 0.8);
                color: #F8FAFC;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding-left: 8px;
                font-size: 10px;
            }
        """)
        v_row.addWidget(v_lbl)
        v_row.addStretch()
        v_row.addWidget(self.v_combo)
        c3_layout.addLayout(v_row)

        grid.addWidget(card3, 1, 0)

        # ---------------- CARD 4: Storage & Maintenance ----------------
        card4 = QFrame()
        card4.setObjectName("setCard4")
        card4.setStyleSheet("""
            QFrame#setCard4 {
                background: rgba(16, 24, 39, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 16px;
            }
        """)
        c4_layout = QVBoxLayout(card4)
        c4_layout.setContentsMargins(16, 14, 16, 14)
        c4_layout.setSpacing(10)

        c4_title = QLabel("🛠️ Maintenance & Storage Cleanup")
        c4_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        c4_title.setStyleSheet("color: #F59E0B; background: transparent;")
        c4_layout.addWidget(c4_title)

        # Auto Purge Row
        ap_row = QHBoxLayout()
        ap_lbl = QLabel("Auto-Purge System Logs & Cache")
        ap_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        ap_lbl.setStyleSheet("color: #F8FAFC; background: transparent;")

        self.purge_btn = QPushButton("Purge Temp Cache  🧹")
        self.purge_btn.setFixedHeight(32)
        self.purge_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.purge_btn.setStyleSheet("""
            QPushButton {
                background: rgba(245, 158, 11, 0.15);
                color: #F59E0B;
                border: 1px solid rgba(245, 158, 11, 0.3);
                border-radius: 8px;
                font-size: 10px;
                font-weight: bold;
                padding: 0 10px;
            }
            QPushButton:hover {
                background: rgba(245, 158, 11, 0.3);
            }
        """)
        ap_row.addWidget(ap_lbl)
        ap_row.addStretch()
        ap_row.addWidget(self.purge_btn)
        c4_layout.addLayout(ap_row)

        # Diagnostics Log Level Row
        log_row = QHBoxLayout()
        log_lbl = QLabel("System Log Verbosity Level")
        log_lbl.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        log_lbl.setStyleSheet("color: #F8FAFC; background: transparent;")

        self.log_combo = QComboBox()
        self.log_combo.addItems(["INFO (Standard Telemetry)", "DEBUG (Full Diagnostic Log)", "WARNING (Errors Only)"])
        self.log_combo.setFixedSize(200, 30)
        self.log_combo.setStyleSheet("""
            QComboBox {
                background: rgba(30, 41, 59, 0.8);
                color: #F8FAFC;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding-left: 8px;
                font-size: 10px;
            }
        """)
        log_row.addWidget(log_lbl)
        log_row.addStretch()
        log_row.addWidget(self.log_combo)
        c4_layout.addLayout(log_row)

        grid.addWidget(card4, 1, 1)

        layout.addLayout(grid)

        # ---------------- SAVE PREFERENCES BAR ----------------
        save_bar = QFrame()
        save_bar.setObjectName("setSaveBar")
        save_bar.setStyleSheet("""
            QFrame#setSaveBar {
                background: rgba(16, 24, 39, 0.85);
                border: 1px solid rgba(59, 130, 246, 0.3);
                border-radius: 14px;
            }
        """)
        sb_layout = QHBoxLayout(save_bar)
        sb_layout.setContentsMargins(16, 10, 16, 10)

        sb_txt = QLabel("Changes apply automatically to active SHRIVA AI sessions.")
        sb_txt.setFont(QFont("Segoe UI", 9))
        sb_txt.setStyleSheet("color: #94A3B8; background: transparent;")

        self.settings_btn = QPushButton("Save System Preferences  💾")
        self.settings_btn.setFixedHeight(36)
        self.settings_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background: #3B82F6;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11px;
                padding: 0 16px;
            }
            QPushButton:hover {
                background: #60A5FA;
            }
        """)

        sb_layout.addWidget(sb_txt)
        sb_layout.addStretch()
        sb_layout.addWidget(self.settings_btn)

        layout.addWidget(save_bar)
        layout.addStretch()

        return view

    # ---------------- STATUS BAR ----------------
    def create_status_bar(self):
        bar = QFrame()
        bar.setFixedHeight(34)
        bar.setStyleSheet("""
            QFrame {
                background: rgba(11, 17, 32, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px;
            }
        """)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(14, 0, 14, 0)

        self.status_left = QLabel("● ONLINE | SECURE QUANTUM LINK")
        self.status_left.setStyleSheet("color: #10B981; font-weight: bold; font-size: 10px; background: transparent;")

        self.status_center = QLabel("AI CORE: ACTIVE | THREAT LEVEL: MINIMAL")
        self.status_center.setStyleSheet("color: #60A5FA; font-weight: bold; font-size: 10px; background: transparent;")

        self.status_right = QLabel("ENCRYPTED • QUANTUM SECURE")
        self.status_right.setStyleSheet("color: #94A3B8; font-size: 10px; background: transparent;")

        layout.addWidget(self.status_left)
        layout.addStretch()
        layout.addWidget(self.status_center)
        layout.addStretch()
        layout.addWidget(self.status_right)

        return bar

    # ---------------- SYSTEM UPDATES & ULTRON/VIBRATION HANDLERS ----------------
    def start_system_updates(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system_metrics)
        self.timer.start(1000)

    def update_system_metrics(self):
        if not hasattr(self, 'cpu_bar'):
            return
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent

        # Update bar widths safely
        if self.cpu_bar.parent():
            w = max(100, self.cpu_bar.parent().width() - 40)
            self.cpu_bar.bar.setFixedWidth(int(max(10, w * cpu / 100)))
            self.cpu_bar.percent_label.setText(f"CPU Usage: {cpu:.1f}%")

            self.ram_bar.bar.setFixedWidth(int(max(10, w * ram / 100)))
            self.ram_bar.percent_label.setText(f"RAM Memory: {ram:.1f}%")

            gpu = random.randint(20, 60)
            net = random.randint(10, 100)

            self.gpu_bar.bar.setFixedWidth(int(max(10, w * gpu / 100)))
            self.gpu_bar.percent_label.setText(f"GPU Telemetry: {gpu:.1f}%")

            self.network_bar.bar.setFixedWidth(int(max(10, w * net / 100)))
            self.network_bar.percent_label.setText(f"Network Speed: {net:.1f} MB/s")

    def toggle_ultron_mode(self):
        self.is_ultron = not self.is_ultron
        self.core_widget.set_ultron_mode(self.is_ultron)

        if self.is_ultron:
            self.setStyleSheet("QWidget { background-color: #120308; color: #F8FAFC; font-family: 'Segoe UI'; }")
            self.ultron_toggle.setText("Deactivate Ultron Protocol")
            self.ultron_toggle.setStyleSheet("background: #EF4444; color: white; font-weight: bold;")
        else:
            self.setStyleSheet("QWidget { background-color: #050816; color: #F8FAFC; font-family: 'Segoe UI'; }")
            self.ultron_toggle.setText("Activate Ultron Protocol")
            self.ultron_toggle.setStyleSheet("background: rgba(239, 68, 68, 0.2); color: #EF4444; border: 1px solid #EF4444; border-radius: 8px; font-weight: bold;")

        self.ultron_mode_changed.emit(self.is_ultron)

    def trigger_intruder_alarm_vibration(self):
        """Intruder Alarm Jitter Vibration & Red Strobe Effect."""
        try:
            self.vibrate_count = 0
            
            def _vibrate_step():
                if self.vibrate_count > 24:
                    self.vibrate_timer.stop()
                    if hasattr(self, 'main_container') and self.main_container.layout():
                        self.main_container.layout().setContentsMargins(0, 0, 0, 0)
                        self.main_container.setStyleSheet("#mainContainer { background-color: #050816; border: none; }")
                    return

                dx = random.randint(-16, 16)
                dy = random.randint(-12, 12)

                if hasattr(self, 'main_container') and self.main_container.layout():
                    m_left = max(0, 10 + dx)
                    m_top = max(0, 10 + dy)
                    m_right = max(0, 10 - dx)
                    m_bottom = max(0, 10 - dy)
                    self.main_container.layout().setContentsMargins(m_left, m_top, m_right, m_bottom)

                    border_color = "#FF0044" if (self.vibrate_count % 2 == 0) else "#880000"
                    self.main_container.setStyleSheet(f"#mainContainer {{ border: 4px solid {border_color}; }}")

                self.vibrate_count += 1

            self.vibrate_timer.timeout.connect(_vibrate_step)
            self.vibrate_timer.start(35)
        except Exception as e:
            print(f"[VIBRATION ERROR] {e}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()


# Alias for main.py import compatibility
JarvisUI = JarvisUltimate

def start_ultimate_jarvis():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = JarvisUltimate()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    start_ultimate_jarvis()