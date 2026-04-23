import sys
import math
import random
import psutil
from datetime import datetime
import os

# Fix DPI scaling before QApplication starts
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"

from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QThread, pyqtSignal
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QFont, QBrush,
    QLinearGradient, QRadialGradient, QConicalGradient, QPainterPath,
    QFontDatabase, QAction
)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTextEdit, QFrame, QGraphicsOpacityEffect,
    QScrollBar, QSystemTrayIcon, QMenu
)

# Set DPI awareness
try:
    from ctypes import windll
    windll.user32.SetProcessDPIAware()
except:
    pass

# ---------------- GLOBAL ANIMATION (Thread Safe) ----------------
class AnimationThread(QThread):
    pulse_updated = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        self.time = 0
        self.running = True
        
    def run(self):
        while self.running:
            self.time += 0.02
            pulse = (math.sin(self.time * 2) + 1) * 0.5
            self.pulse_updated.emit(pulse)
            self.msleep(20)
    
    def stop(self):
        self.running = False

anim_thread = AnimationThread()
global_pulse = 0.5

# ---------------- HOLOGRAPHIC ARC REACTOR ----------------
class HolographicReactor(QWidget):
    def __init__(self):
        super().__init__()
        self.angle = 0
        self.inner_angle = 0
        self.pulse = 0.5
        self.particles = [(random.uniform(-100, 100), random.uniform(-100, 100)) for _ in range(30)]
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)
        
        anim_thread.pulse_updated.connect(self.update_pulse)

    def update_pulse(self, pulse):
        self.pulse = pulse
        self.update()

    def update_animation(self):
        self.angle = (self.angle + 2) % 360
        self.inner_angle = (self.inner_angle - 1.5) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center = self.rect().center()
        painter.translate(center)

        # Outer Energy Field
        for layer in range(4):
            size = 100 + layer * 12 + self.pulse * 8
            alpha = max(0, 30 - layer * 8)
            
            gradient = QRadialGradient(QPointF(0, 0), size)
            gradient.setColorAt(0, QColor(0, 255, 255, alpha))
            gradient.setColorAt(0.7, QColor(0, 150, 255, alpha//2))
            gradient.setColorAt(1, QColor(0, 50, 150, 0))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(-size/2, -size/2, size, size))

        # Main Rings
        for i in range(5):
            painter.save()
            painter.rotate(self.angle + i * 72)
            
            gradient = QConicalGradient(QPointF(0, 0), self.angle + i * 30)
            gradient.setColorAt(0, QColor("#00ffff"))
            gradient.setColorAt(0.3, QColor("#0088ff"))
            gradient.setColorAt(0.6, QColor("#00ffff"))
            gradient.setColorAt(1, QColor("#0044ff"))
            
            pen = QPen(QBrush(gradient), 3 + i * 0.5)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QRectF(-70 + i*8, -60 + i*6, 140 - i*16, 120 - i*12))
            painter.restore()

        # Inner Core
        painter.save()
        painter.rotate(self.inner_angle)
        
        core_gradient = QRadialGradient(QPointF(0, 0), 35)
        core_gradient.setColorAt(0, QColor(255, 255, 255, 200))
        core_gradient.setColorAt(0.5, QColor(0, 255, 255, 150))
        core_gradient.setColorAt(1, QColor(0, 100, 255, 50))
        
        painter.setBrush(QBrush(core_gradient))
        painter.setPen(QPen(QColor("#00ffff"), 2))
        
        path = QPainterPath()
        for j in range(3):
            angle = j * 120 + self.angle
            x = 20 * math.cos(math.radians(angle))
            y = 20 * math.sin(math.radians(angle))
            if j == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        path.closeSubpath()
        painter.drawPath(path)
        painter.restore()

        # Particles
        painter.setPen(QPen(QColor("#00ffff"), 2))
        for px, py in self.particles:
            dist = math.sqrt(px**2 + py**2)
            if dist < 100:
                alpha = int(255 * (1 - dist/100) * (0.5 + 0.5 * self.pulse))
                painter.setBrush(QBrush(QColor(0, 255, 255, alpha)))
                painter.drawEllipse(QPointF(px, py), 2, 2)

# ---------------- MATRIX RAIN (Optimized) ----------------
class MatrixRain(QWidget):
    def __init__(self):
        super().__init__()
        self.columns = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_rain)
        self.timer.start(50)
        self.init_columns()

    def init_columns(self):
        self.columns = []
        for _ in range(40):
            self.columns.append({
                'x': random.randint(0, 1920),
                'y': random.randint(-500, 0),
                'speed': random.randint(5, 15),
                'chars': [random.choice("01") for _ in range(15)]
            })

    def update_rain(self):
        for col in self.columns:
            col['y'] += col['speed']
            if col['y'] > 1080:
                col['y'] = random.randint(-200, 0)
                col['x'] = random.randint(0, 1920)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(QFont("Consolas", 12))
        
        for col in self.columns:
            for i, char in enumerate(col['chars']):
                y_pos = col['y'] - i * 18
                if 0 <= y_pos <= self.height():
                    alpha = max(0, 200 - i * 25)
                    if alpha > 0:
                        color = QColor(0, 255, 150, alpha) if i == 0 else QColor(0, 150, 100, alpha)
                        painter.setPen(QPen(color))
                        painter.drawText(col['x'], int(y_pos), char)

# ---------------- 3D HOLOGRAPHIC GLOBE ----------------
class HolographicGlobe(QWidget):
    def __init__(self):
        super().__init__()
        self.rotation_x = 0
        self.rotation_y = 0
        self.rotation_z = 0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        self.timer.start(40)

    def rotate(self):
        self.rotation_x = (self.rotation_x + 1) % 360
        self.rotation_y = (self.rotation_y + 1.5) % 360
        self.rotation_z = (self.rotation_z + 0.5) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center = self.rect().center()
        painter.translate(center)

        painter.save()
        painter.rotate(self.rotation_x)
        painter.rotate(self.rotation_y)
        
        gradient = QRadialGradient(QPointF(0, 0), 80)
        gradient.setColorAt(0, QColor(0, 100, 255, 100))
        gradient.setColorAt(0.7, QColor(0, 50, 150, 80))
        gradient.setColorAt(1, QColor(0, 20, 80, 50))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor("#00ffff"), 1.5))
        painter.drawEllipse(QRectF(-80, -80, 160, 160))
        
        painter.setPen(QPen(QColor(0, 255, 255, 60), 1))
        for lat in range(-60, 61, 30):
            painter.save()
            painter.rotate(lat)
            painter.drawEllipse(QRectF(-80, -20, 160, 40))
            painter.restore()
        
        for lon in range(0, 360, 30):
            painter.save()
            painter.rotate(lon)
            painter.drawLine(0, -80, 0, 80)
            painter.restore()
        
        painter.restore()
        
        painter.save()
        painter.rotate(self.rotation_z * 2)
        painter.setPen(QPen(QColor("#00ffff"), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(-95, -95, 190, 190))
        painter.restore()

# ---------------- NEURAL NETWORK ----------------
class NeuralNetworkViz(QWidget):
    def __init__(self):
        super().__init__()
        self.nodes_layer1 = [(50, i*35+25) for i in range(5)]
        self.nodes_layer2 = [(150, i*30+20) for i in range(8)]
        self.nodes_layer3 = [(250, i*35+25) for i in range(5)]
        self.pulse_offset = 0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)

    def animate(self):
        self.pulse_offset = (self.pulse_offset + 0.1) % (2 * math.pi)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw connections
        for i, n1 in enumerate(self.nodes_layer1):
            for j, n2 in enumerate(self.nodes_layer2):
                alpha = int(80 + 100 * (math.sin(self.pulse_offset + i*0.5 + j*0.3) * 0.5 + 0.5))
                painter.setPen(QPen(QColor(0, 255, 255, alpha), 1))
                painter.drawLine(int(n1[0]), int(n1[1]), int(n2[0]), int(n2[1]))
        
        for i, n2 in enumerate(self.nodes_layer2):
            for j, n3 in enumerate(self.nodes_layer3):
                alpha = int(80 + 100 * (math.sin(self.pulse_offset + i*0.4 + j*0.6) * 0.5 + 0.5))
                painter.setPen(QPen(QColor(0, 200, 255, alpha), 1))
                painter.drawLine(int(n2[0]), int(n2[1]), int(n3[0]), int(n3[1]))
        
        # Draw nodes
        for nodes, size in [(self.nodes_layer1, 6), (self.nodes_layer2, 8), (self.nodes_layer3, 6)]:
            for x, y in nodes:
                gradient = QRadialGradient(QPointF(x, y), size * 2)
                gradient.setColorAt(0, QColor(0, 255, 255, 200))
                gradient.setColorAt(1, QColor(0, 100, 255, 50))
                
                painter.setBrush(QBrush(gradient))
                painter.setPen(QPen(QColor("#00ffff"), 2))
                painter.drawEllipse(QPointF(x, y), size, size)

# ---------------- PREMIUM TERMINAL ----------------
class PremiumTerminal(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 11))
        self.setStyleSheet("""
            QTextEdit {
                background-color: rgba(2, 6, 23, 200);
                color: #00ffcc;
                border: 2px solid #00ffff;
                border-radius: 12px;
                padding: 12px;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #00ffff;
                border-radius: 4px;
            }
        """)
        
        self.append_message("JARVIS", "System initialization complete.")
        self.append_message("JARVIS", "Welcome back, Sir.")

    def append_message(self, sender, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        if sender == "JARVIS":
            self.append(f'<span style="color: #00ffff; font-weight: bold;">[{timestamp}] {sender}:</span> <span style="color: #e0e0e0;">{message}</span>')
        else:
            self.append(f'<span style="color: #ffaa00; font-weight: bold;">[{timestamp}] {sender}:</span> <span style="color: #ffffff;">{message}</span>')

# ---------------- MAIN JARVIS UI ----------------
class JarvisUI(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("J.A.R.V.I.S ULTIMATE")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Get screen size
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #020617, stop:0.5 #0a0e27, stop:1 #020617);
            }
        """)
        
        self.init_ui()
        
        # Start animation thread
        anim_thread.start()
        
        # Start system tray
        self.setup_tray()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)
        
        # Matrix Rain Background
        self.matrix_rain = MatrixRain()
        self.matrix_rain.setParent(self)
        self.matrix_rain.lower()
        self.matrix_rain.setGeometry(self.rect())
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Content Grid
        content_grid = QGridLayout()
        content_grid.setSpacing(15)
        
        # Left Panel
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        
        self.reactor = HolographicReactor()
        self.reactor.setMinimumSize(320, 320)
        
        self.globe = HolographicGlobe()
        self.globe.setMinimumSize(320, 220)
        
        left_panel.addWidget(self.reactor, 2)
        left_panel.addWidget(self.globe, 1)
        
        # Center Panel
        center_panel = QVBoxLayout()
        center_panel.setSpacing(15)
        
        self.neural_net = NeuralNetworkViz()
        self.neural_net.setMinimumSize(380, 280)
        
        stats_panel = self.create_stats_panel()
        
        center_panel.addWidget(self.neural_net, 2)
        center_panel.addWidget(stats_panel, 1)
        
        # Right Panel
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        self.terminal = PremiumTerminal()
        
        control_panel = self.create_control_panel()
        
        right_panel.addWidget(self.terminal, 3)
        right_panel.addWidget(control_panel, 1)
        
        content_grid.addLayout(left_panel, 0, 0)
        content_grid.addLayout(center_panel, 0, 1)
        content_grid.addLayout(right_panel, 0, 2)
        
        content_grid.setColumnStretch(0, 2)
        content_grid.setColumnStretch(1, 2)
        content_grid.setColumnStretch(2, 3)
        
        main_layout.addLayout