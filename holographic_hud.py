import math
import psutil
from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QGuiApplication
from PyQt6.QtWidgets import QDialog, QApplication, QPushButton, QHBoxLayout, QVBoxLayout, QWidget
from voice_engine import speak

class HolographicHUDOverlay(QDialog):
    """
    Iron Man Holographic Heads-Up Display (HUD) Overlay.
    Futuristic cybernetic overlay with rotating arc-reactor rings,
    live hardware telemetry, target brackets, and pulsing audio equalizer.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("JARVIS HOLOGRAPHIC HUD")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        screen = QGuiApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())

        self.angle = 0.0
        self.pulse = 0.0
        self.cpu_load = 15.0
        self.ram_load = 45.0

        # Animation Timer ~30 FPS
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._animate_step)
        self.anim_timer.start(33)

        # Telemetry Timer ~1s
        self.stat_timer = QTimer(self)
        self.stat_timer.timeout.connect(self._update_stats)
        self.stat_timer.start(1000)

        # Colors
        self.cyan_core = QColor(0, 255, 255, 230)
        self.cyan_dim = QColor(0, 255, 255, 90)
        self.gold_accent = QColor(255, 200, 50, 210)

        # Exit HUD floating button at top right
        self._init_controls()

    def _init_controls(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(25, 20, 25, 20)

        top_row = QHBoxLayout()
        top_row.addStretch()

        close_btn = QPushButton("✕ DISENGAGE HUD")
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(15, 23, 42, 0.85);
                color: #00ffff;
                border: 1.5px solid #00ffff;
                border-radius: 8px;
                padding: 6px 16px;
                font-family: 'Consolas', monospace;
                font-weight: bold;
                font-size: 11px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.7);
                border-color: #ffffff;
                color: #ffffff;
            }
        """)
        close_btn.clicked.connect(self.close)
        top_row.addWidget(close_btn)

        root_layout.addLayout(top_row)
        root_layout.addStretch()

    def _animate_step(self):
        self.angle = (self.angle + 2.0) % 360
        self.pulse = (self.pulse + 0.12) % (2 * math.pi)
        self.update()

    def _update_stats(self):
        try:
            self.cpu_load = psutil.cpu_percent()
            self.ram_load = psutil.virtual_memory().percent
        except Exception:
            pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Semi-translucent dark vignette
        painter.fillRect(self.rect(), QColor(2, 6, 23, 50))

        # 1. Sci-Fi Corner Brackets
        pen_bracket = QPen(self.cyan_dim, 2)
        painter.setPen(pen_bracket)
        corner_len = 50

        # Top-Left
        painter.drawLine(30, 30, 30 + corner_len, 30)
        painter.drawLine(30, 30, 30, 30 + corner_len)
        # Top-Right
        painter.drawLine(w - 30, 30, w - 30 - corner_len, 30)
        painter.drawLine(w - 30, 30, w - 30, 30 + corner_len)
        # Bottom-Left
        painter.drawLine(30, h - 30, 30 + corner_len, h - 30)
        painter.drawLine(30, h - 30, 30, h - 30 - corner_len)
        # Bottom-Right
        painter.drawLine(w - 30, h - 30, w - 30 - corner_len, h - 30)
        painter.drawLine(w - 30, h - 30, w - 30, h - 30 - corner_len)

        # 2. Top Banner Header
        painter.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        painter.setPen(self.cyan_core)
        header_text = "⚡ JARVIS OS [MARK VII]  |  INTEGRITY: 100%  |  ENCRYPTION: AES-256-GCM  |  DEFENSE: ARMED"
        painter.drawText(w // 2 - 380, 42, header_text)

        painter.setPen(QPen(self.cyan_dim, 1))
        painter.drawLine(w // 2 - 420, 52, w // 2 + 420, 52)

        # 3. Rotating Arc Reactor Widget (Top-Right: w - 160, 160)
        rx, ry = w - 160, 160
        rad = 55

        # Outer Rotating Ticks
        for i in range(12):
            th = math.radians(i * 30 + self.angle)
            x1 = rx + (rad + 8) * math.cos(th)
            y1 = ry + (rad + 8) * math.sin(th)
            x2 = rx + (rad + 16) * math.cos(th)
            y2 = ry + (rad + 16) * math.sin(th)
            painter.setPen(QPen(self.gold_accent if i % 3 == 0 else self.cyan_dim, 1.5))
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # Counter-rotating Inner Arc
        painter.setPen(QPen(self.cyan_core, 2))
        start_angle = int((self.angle * 2.5) % 360 * 16)
        painter.drawArc(QRectF(rx - rad, ry - rad, rad * 2, rad * 2), start_angle, 120 * 16)
        painter.drawArc(QRectF(rx - rad, ry - rad, rad * 2, rad * 2), start_angle + 180 * 16, 90 * 16)

        # Center Core
        painter.setBrush(QColor(0, 255, 255, 70))
        painter.setPen(QPen(self.cyan_core, 1.5))
        core_r = 16 + 2 * math.sin(self.pulse)
        painter.drawEllipse(QPointF(rx, ry), core_r, core_r)

        painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        painter.drawText(int(rx - 28), int(ry + rad + 24), "ARC REACTOR")

        # 4. Telemetry Gauges (Bottom-Left: 60, h - 120)
        bx, by = 60, h - 120
        painter.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        painter.setPen(self.cyan_core)
        painter.drawText(bx, by, f"CPU UTILIZATION: {self.cpu_load:.1f}%")

        painter.setPen(QPen(self.cyan_dim, 1))
        painter.drawRect(bx, by + 8, 180, 8)
        painter.fillRect(bx + 1, by + 9, int(1.78 * min(100, self.cpu_load)), 6, self.cyan_core)

        painter.setPen(self.cyan_core)
        painter.drawText(bx, by + 34, f"RAM OCCUPANCY:   {self.ram_load:.1f}%")
        painter.setPen(QPen(self.cyan_dim, 1))
        painter.drawRect(bx, by + 42, 180, 8)
        painter.fillRect(bx + 1, by + 43, int(1.78 * min(100, self.ram_load)), 6, self.gold_accent)

        # 5. Pulsing Audio Waveform Visualizer (Bottom Center)
        cx = w // 2
        cy = h - 55
        bar_count = 28
        bar_width = 4
        gap = 5
        start_x = cx - ((bar_count * (bar_width + gap)) // 2)

        for i in range(bar_count):
            amp = math.sin(self.pulse * 2 + i * 0.4)
            bar_h = int(6 + abs(amp) * 24)
            px = start_x + i * (bar_width + gap)
            py = cy - (bar_h // 2)

            col = self.cyan_core if i % 2 == 0 else self.gold_accent
            painter.fillRect(px, py, bar_width, bar_h, col)

        painter.setFont(QFont("Consolas", 8))
        painter.setPen(self.cyan_dim)
        painter.drawText(cx - 70, cy + 24, "AUDIO TELEMETRY ACTIVE")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


# Global instances for standalone or bridge usage
active_hud_window = None

def launch_hud_window():
    global active_hud_window
    if not active_hud_window:
        active_hud_window = HolographicHUDOverlay()
    active_hud_window.showFullScreen()
    active_hud_window.raise_()
    return active_hud_window

def close_hud_window():
    global active_hud_window
    if active_hud_window:
        active_hud_window.close()
        active_hud_window = None
