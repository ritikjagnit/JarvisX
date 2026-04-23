import sys
import math
import random
import psutil
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer, QRectF, QPointF, QEasingCurve, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QFont, QBrush, QFontDatabase,
    QLinearGradient, QRadialGradient, QConicalGradient, QPainterPath,
    QPixmap, QImage, QTransform
)
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTextEdit, QFrame, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect, QScrollBar
)

# GLOBAL ANIMATION CONTROLLER
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

# Delay instantiation to avoid timer-thread warnings
anim_controller = None

# ---------------- HOLOGRAPHIC ARC REACTOR ----------------
class HolographicReactor(QWidget):
    def __init__(self):
        super().__init__()
        self.angle = 0
        self.inner_angle = 0
        self.particles = [(random.uniform(-100, 100), random.uniform(-100, 100)) for _ in range(50)]
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)

    def update_animation(self):
        self.angle += 2
        self.inner_angle -= 1.5
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        center = self.rect().center()
        painter.translate(center)

        pulse = anim_controller.global_pulse if anim_controller else 0
        
        # Outer Energy Field
        for layer in range(5):
            size = 100 + layer * 15 + pulse * 10
            gradient = QRadialGradient(QPointF(0, 0), size)
            gradient.setColorAt(0, QColor(0, 255, 255, 30 - layer * 5))
            gradient.setColorAt(0.7, QColor(0, 150, 255, 10))
            gradient.setColorAt(1, QColor(0, 50, 150, 0))
            
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QRectF(-size/2, -size/2, size, size))

        # Main Rings with 3D effect
        for i in range(5):
            painter.save()
            painter.rotate(self.angle + i * 72)
            
            # Create metallic gradient
            gradient = QConicalGradient(QPointF(0, 0), self.angle + i * 30)
            gradient.setColorAt(0, QColor("#00ffff"))
            gradient.setColorAt(0.3, QColor("#0088ff"))
            gradient.setColorAt(0.6, QColor("#00ffff"))
            gradient.setColorAt(1, QColor("#0044ff"))
            
            pen = QPen(QBrush(gradient), 3 + i * 0.5)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            
            # Elliptical for 3D effect
            painter.drawEllipse(QRectF(-70 + i*8, -60 + i*6, 140 - i*16, 120 - i*12))
            painter.restore()

        # Inner Core
        painter.save()
        painter.rotate(self.inner_angle)
        core_gradient = QRadialGradient(QPointF(0, 0), 40)
        core_gradient.setColorAt(0, QColor(255, 255, 255, 200))
        core_gradient.setColorAt(0.5, QColor(0, 255, 255, 150))
        core_gradient.setColorAt(1, QColor(0, 100, 255, 50))
        
        painter.setBrush(QBrush(core_gradient))
        painter.setPen(QPen(QColor("#00ffff"), 2))
        
        # Triangular core
        path = QPainterPath()
        for j in range(3):
            angle = j * 120 + self.angle
            x = 25 * math.cos(math.radians(angle))
            y = 25 * math.sin(math.radians(angle))
            if j == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        path.closeSubpath()
        painter.drawPath(path)
        painter.restore()

        # Floating Particles
        painter.setPen(QPen(QColor("#00ffff"), 2))
        painter.setBrush(QBrush(QColor("#00ffff")))
        for px, py in self.particles:
            dist = math.sqrt(px**2 + py**2)
            if dist < 100:
                alpha = int(255 * (1 - dist/100) * (0.5 + 0.5 * pulse))
                painter.setBrush(QBrush(QColor(0, 255, 255, alpha)))
                painter.drawEllipse(QPointF(px, py), 2, 2)

# ---------------- MATRIX DIGITAL RAIN ----------------
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
        for _ in range(50):
            self.columns.append({
                'x': random.randint(0, 1920),
                'y': random.randint(-500, 0),
                'speed': random.randint(5, 15),
                'chars': [random.choice("01アイウエオカキクケコ") for _ in range(20)]
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
        painter.setFont(QFont("Consolas", 14))
        
        for col in self.columns:
            for i, char in enumerate(col['chars']):
                y_pos = col['y'] - i * 20
                if 0 <= y_pos <= self.height():
                    alpha = 255 - i * 30
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
        self.rotation_x += 1
        self.rotation_y += 1.5
        self.rotation_z += 0.5
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center = self.rect().center()
        painter.translate(center)

        # Draw 3D Globe
        painter.save()
        painter.rotate(self.rotation_x)
        painter.rotate(self.rotation_y)
        
        # Globe gradient
        gradient = QRadialGradient(QPointF(0, 0), 80)
        gradient.setColorAt(0, QColor(0, 100, 255, 100))
        gradient.setColorAt(0.7, QColor(0, 50, 150, 80))
        gradient.setColorAt(1, QColor(0, 20, 80, 50))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor("#00ffff"), 1.5))
        painter.drawEllipse(QRectF(-80, -80, 160, 160))
        
        # Latitude lines
        painter.setPen(QPen(QColor(0, 255, 255, 80), 1))
        for lat in range(-60, 61, 30):
            painter.save()
            painter.rotate(lat)
            painter.drawEllipse(QRectF(-80, -20, 160, 40))
            painter.restore()
        
        # Longitude lines
        for lon in range(0, 360, 30):
            painter.save()
            painter.rotate(lon)
            painter.drawLine(0, -80, 0, 80)
            painter.restore()
        
        painter.restore()
        
        # Outer rings
        painter.save()
        painter.rotate(self.rotation_z * 2)
        painter.setPen(QPen(QColor("#00ffff"), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(-95, -95, 190, 190))
        painter.restore()

# ---------------- NEURAL NETWORK VISUALIZER ----------------
class NeuralNetworkViz(QWidget):
    def __init__(self):
        super().__init__()
        self.nodes_layer1 = [(50, i*40+30) for i in range(5)]
        self.nodes_layer2 = [(150, i*40+30) for i in range(8)]
        self.nodes_layer3 = [(250, i*40+30) for i in range(5)]
        self.connections = []
        self.pulse_offset = 0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)

    def animate(self):
        self.pulse_offset += 0.1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pulse = anim_controller.global_pulse if anim_controller else 0
        
        # Draw connections with pulse effect
        for i, n1 in enumerate(self.nodes_layer1):
            for j, n2 in enumerate(self.nodes_layer2):
                alpha = int(100 + 155 * (math.sin(self.pulse_offset + i*0.5 + j*0.3) * 0.5 + 0.5))
                painter.setPen(QPen(QColor(0, 255, 255, alpha), 1))
                painter.drawLine(int(n1[0]), int(n1[1]), int(n2[0]), int(n2[1]))
        
        for i, n2 in enumerate(self.nodes_layer2):
            for j, n3 in enumerate(self.nodes_layer3):
                alpha = int(100 + 155 * (math.sin(self.pulse_offset + i*0.4 + j*0.6) * 0.5 + 0.5))
                painter.setPen(QPen(QColor(0, 200, 255, alpha), 1))
                painter.drawLine(int(n2[0]), int(n2[1]), int(n3[0]), int(n3[1]))
        
        # Draw nodes
        for nodes, size in [(self.nodes_layer1, 8), (self.nodes_layer2, 10), (self.nodes_layer3, 8)]:
            for x, y in nodes:
                gradient = QRadialGradient(QPointF(x, y), size * 2)
                gradient.setColorAt(0, QColor(0, 255, 255, 200))
                gradient.setColorAt(1, QColor(0, 100, 255, 50))
                
                painter.setBrush(QBrush(gradient))
                painter.setPen(QPen(QColor("#00ffff"), 2))
                painter.drawEllipse(QPointF(x, y), size, size)

# ---------------- ULTRA PREMIUM CHAT TERMINAL ----------------
class PremiumTerminal(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 12))
        self.setStyleSheet("""
            QTextEdit {
                background-color: rgba(2, 6, 23, 0.7);
                color: #00ffcc;
                border: 2px solid #00ffff;
                border-radius: 15px;
                padding: 15px;
                font-size: 13px;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #00ffff, stop:1 #0066ff);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        self.append_message("JARVIS", "System initialization complete. All cores operational.")
        self.append_message("JARVIS", "Welcome back, Sir. Ready for your commands.")

    def append_message(self, sender, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        if sender == "JARVIS":
            self.append(f'<span style="color: #00ffff; font-weight: bold;">[{timestamp}] {sender}:</span> <span style="color: #e0e0e0;">{message}</span>')
        else:
            self.append(f'<span style="color: #ffaa00; font-weight: bold;">[{timestamp}] {sender}:</span> <span style="color: #ffffff;">{message}</span>')

# ---------------- MAIN JARVIS WINDOW ----------------
class JarvisUltimate(QWidget):
    @property
    def chat_box(self): return self.terminal
    @property
    def send_button(self): return getattr(self, 'execute_btn', None)

    def __init__(self):
        super().__init__()
        
        # Full Screen Setup
        self.setWindowTitle("J.A.R.V.I.S ULTIMATE")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showMaximized()
        
        # Enable escape to exit fullscreen
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Main Layout
        self.main_container = QFrame()
        self.main_container.setObjectName("mainContainer")
        self.main_container.setStyleSheet("""
            #mainContainer {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #020617, stop:0.5 #0a0e27, stop:1 #020617);
                border: 2px solid #00ffff;
                border-radius: 0px;
            }
        """)
        
        main_layout = QVBoxLayout(self.main_container)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Add Matrix Rain Background (as overlay)
        self.matrix_rain = MatrixRain()
        self.matrix_rain.setParent(self.main_container)
        self.matrix_rain.lower()
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Main Content Grid
        content_grid = QGridLayout()
        content_grid.setSpacing(15)
        
        # Left Panel - Visualizations
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        
        self.reactor = HolographicReactor()
        self.reactor.setMinimumSize(350, 350)
        
        self.globe = HolographicGlobe()
        self.globe.setMinimumSize(350, 250)
        
        left_panel.addWidget(self.reactor, 2)
        left_panel.addWidget(self.globe, 1)
        
        # Center Panel - Neural Network
        center_panel = QVBoxLayout()
        center_panel.setSpacing(15)
        
        self.neural_net = NeuralNetworkViz()
        self.neural_net.setMinimumSize(400, 300)
        
        # Stats Panel
        stats_panel = self.create_stats_panel()
        
        center_panel.addWidget(self.neural_net, 2)
        center_panel.addWidget(stats_panel, 1)
        
        # Right Panel - Terminal & Controls
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        self.terminal = PremiumTerminal()
        
        self.input_box = QTextEdit()
        self.input_box.setFixedHeight(40)
        self.input_box.setPlaceholderText("System command override...")
        self.input_box.setStyleSheet("background: rgba(2, 6, 23, 0.7); color: #00ffff; border: 1px solid #0066ff; border-radius: 5px; padding: 5px;")
        
        control_panel = self.create_control_panel()
        
        right_panel.addWidget(self.terminal, 3)
        right_panel.addWidget(self.input_box)
        right_panel.addWidget(control_panel, 1)
        
        # Add to grid
        content_grid.addLayout(left_panel, 0, 0)
        content_grid.addLayout(center_panel, 0, 1)
        content_grid.addLayout(right_panel, 0, 2)
        
        content_grid.setColumnStretch(0, 2)
        content_grid.setColumnStretch(1, 2)
        content_grid.setColumnStretch(2, 3)
        
        main_layout.addLayout(content_grid, 1)
        
        # Status Bar
        status_bar = self.create_status_bar()
        main_layout.addWidget(status_bar)
        
        # Final setup
        window_layout = QVBoxLayout(self)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.addWidget(self.main_container)
        self.setLayout(window_layout)
        
        # Start updates
        self.start_system_updates()

    def create_header(self):
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.3);
                border-bottom: 1px solid #00ffff;
                border-radius: 0px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 0, 30, 0)
        
        # Animated Title
        title = QLabel("J.A.R.V.I.S")
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title.setStyleSheet("""
            color: #00ffff;
        """)
        
        # Status indicators
        status_layout = QHBoxLayout()
        indicators = ["SYSTEM", "AI CORE", "DEFENSE", "ENERGY"]
        for ind in indicators:
            label = QLabel(f"● {ind}")
            label.setFont(QFont("Arial", 12))
            label.setStyleSheet("color: #00ff88;")
            status_layout.addWidget(label)
        
        # Time display
        self.time_label = QLabel()
        self.time_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.time_label.setStyleSheet("color: #ffffff;")
        
        # Close button
        close_btn = QPushButton("✕ EXIT")
        close_btn.setFixedSize(100, 40)
        close_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff0066, stop:1 #cc0033);
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff3366, stop:1 #ff0033);
            }
        """)
        close_btn.clicked.connect(self.close)
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addLayout(status_layout)
        layout.addStretch()
        layout.addWidget(self.time_label)
        layout.addWidget(close_btn)
        
        return header

    def create_stats_panel(self):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(15, 23, 42, 0.7);
                border: 1.5px solid #00ffff;
                border-radius: 15px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        
        title = QLabel("SYSTEM METRICS")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff; border: none;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create metric bars
        self.cpu_bar = self.create_metric_bar("CPU")
        self.ram_bar = self.create_metric_bar("RAM")
        self.gpu_bar = self.create_metric_bar("GPU")
        self.network_bar = self.create_metric_bar("NETWORK")
        
        layout.addWidget(title)
        layout.addWidget(self.cpu_bar)
        layout.addWidget(self.ram_bar)
        layout.addWidget(self.gpu_bar)
        layout.addWidget(self.network_bar)
        
        return panel

    def create_metric_bar(self, name):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        
        label = QLabel(name)
        label.setFont(QFont("Arial", 10))
        label.setStyleSheet("color: #94a3b8; border: none;")
        
        bar_frame = QFrame()
        bar_frame.setFixedHeight(25)
        bar_frame.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.5);
                border: 1px solid #00ffff;
                border-radius: 5px;
            }
        """)
        
        bar = QFrame(bar_frame)
        bar.setFixedHeight(23)
        bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ffff, stop:1 #0066ff);
                border-radius: 4px;
            }
        """)
        
        layout.addWidget(label)
        layout.addWidget(bar_frame)
        
        widget.bar = bar
        widget.percent_label = label
        return widget

    def create_control_panel(self):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background: rgba(15, 23, 42, 0.7);
                border: 1.5px solid #00ffff;
                border-radius: 15px;
            }
        """)
        
        layout = QGridLayout(panel)
        layout.setSpacing(10)
        
        buttons = [
            ("🎤 VOICE", 0, 0), ("⚡ EXECUTE", 0, 1),
            ("🔍 SCAN", 1, 0), ("🛡️ DEFENSE", 1, 1),
            ("📊 ANALYTICS", 2, 0), ("⚙️ SETTINGS", 2, 1)
        ]
        
        for text, row, col in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(45)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(0, 255, 255, 0.1);
                    color: #00ffff;
                    border: 2px solid #00ffff;
                    border-radius: 10px;
                    font-weight: bold;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background: rgba(0, 255, 255, 0.3);
                    border: 2px solid #ffffff;
                    color: white;
                }
            """)
            layout.addWidget(btn, row, col)
            
            if text == "⚡ EXECUTE":
                self.execute_btn = btn
            elif text == "🎤 VOICE":
                self.voice_button = btn
            elif "SCAN" in text:
                self.scan_btn = btn
            elif "DEFENSE" in text:
                self.defense_btn = btn
            elif "ANALYTICS" in text:
                self.analytics_btn = btn
            elif "SETTINGS" in text:
                self.settings_btn = btn
        
        return panel

    def create_status_bar(self):
        bar = QFrame()
        bar.setFixedHeight(40)
        bar.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.5);
                border-top: 1px solid #00ffff;
            }
        """)
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(20, 0, 20, 0)
        
        self.status_left = QLabel("● ONLINE | SECURE CONNECTION")
        self.status_left.setStyleSheet("color: #00ff88; font-weight: bold;")
        
        self.status_center = QLabel("AI CORE: ACTIVE | THREAT LEVEL: MINIMAL")
        self.status_center.setStyleSheet("color: #00ffff;")
        self.status_center.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.status_right = QLabel("ENCRYPTED • QUANTUM SECURE")
        self.status_right.setStyleSheet("color: #94a3b8;")
        
        layout.addWidget(self.status_left)
        layout.addStretch()
        layout.addWidget(self.status_center)
        layout.addStretch()
        layout.addWidget(self.status_right)
        
        return bar

    def start_system_updates(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system_metrics)
        self.timer.start(1000)
        
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)

    def update_system_metrics(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        
        # Update bars
        self.cpu_bar.bar.setFixedWidth(int(23 + (self.cpu_bar.parent().width() - 40) * cpu / 100))
        self.cpu_bar.percent_label.setText(f"CPU: {cpu:.1f}%")
        
        self.ram_bar.bar.setFixedWidth(int(23 + (self.ram_bar.parent().width() - 40) * ram / 100))
        self.ram_bar.percent_label.setText(f"RAM: {ram:.1f}%")
        
        # Simulate GPU and Network
        gpu = random.randint(20, 60)
        network = random.randint(10, 100)
        
        self.gpu_bar.bar.setFixedWidth(int(23 + (self.gpu_bar.parent().width() - 40) * gpu / 100))
        self.gpu_bar.percent_label.setText(f"GPU: {gpu:.1f}%")
        
        self.network_bar.bar.setFixedWidth(int(23 + (self.network_bar.parent().width() - 40) * network / 100))
        self.network_bar.percent_label.setText(f"NETWORK: {network:.1f} MB/s")

    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.time_label.setText(f"{current_date} | {current_time}")

    def execute_command(self):
        commands = [
            "Running system diagnostic... All systems nominal.",
            "Scanning network perimeter... No threats detected.",
            "Optimizing AI neural pathways... Performance increased by 23%.",
            "Checking security protocols... All firewalls active.",
            "Updating database... Synchronization complete."
        ]
        self.terminal.append_message("JARVIS", random.choice(commands))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

# ---------------- MAIN EXECUTION ----------------
JarvisUI = JarvisUltimate

def start_ultimate_jarvis():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set custom font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = JarvisUltimate()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    start_ultimate_jarvis()