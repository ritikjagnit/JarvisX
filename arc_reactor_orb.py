import sys
import math
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QRadialGradient, QPolygonF
from PyQt6.QtWidgets import QWidget, QMenu, QApplication

class ArcReactorOrb(QWidget):
    """
    Iron Man Mark VII Floating Arc Reactor Desktop Orb.
    A frameless, draggable, always-on-top transparent cyber widget
    featuring a rotating palladium core, pulsing HUD energy rings,
    and a quick-access Stark Industries contextual control suite.
    """
    voice_toggled = pyqtSignal()
    open_dashboard = pyqtSignal()
    trigger_action = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(165, 170)

        # Position at top right corner of primary screen by default
        screen = QApplication.primaryScreen()
        if screen:
            geom = screen.availableGeometry()
            self.move(geom.width() - 190, 45)

        # Animation states
        self.outer_angle = 0.0
        self.inner_angle = 0.0
        self.pulse_phase = 0.0
        self.is_listening = False
        self.status_text = "SHRIVA AI // ONLINE"

        # Dragging support
        self.drag_position = QPoint()

        # 30 FPS Render Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_animation)
        self.timer.start(33)

    def _update_animation(self):
        speed_mult = 2.5 if self.is_listening else 1.0
        self.outer_angle = (self.outer_angle + 1.2 * speed_mult) % 360.0
        self.inner_angle = (self.inner_angle - 2.0 * speed_mult) % 360.0
        self.pulse_phase = (self.pulse_phase + 0.08 * speed_mult) % (2.0 * math.pi)
        self.update()

    def set_listening_state(self, listening: bool):
        self.is_listening = listening
        self.status_text = "LISTENING..." if listening else "SHRIVA AI // ONLINE"
        self.update()

    # --- Mouse Drag & Click Handling ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_dashboard.emit()

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(10, 18, 30, 0.95);
                color: #e2e8f0;
                border: 1px solid #00f0ff;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Segoe UI', Consolas;
                font-size: 11px;
            }
            QMenu::item {
                padding: 6px 20px 6px 12px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: rgba(0, 240, 255, 0.25);
                color: #00ffff;
            }
            QMenu::separator {
                height: 1px;
                background: #1e293b;
                margin: 4px 0px;
            }
        """)

        act_voice = menu.addAction("🎙️ Toggle Voice Listening")
        act_dashboard = menu.addAction("💻 Open Full Dashboard")
        menu.addSeparator()

        act_hud = menu.addAction("📊 Holographic HUD (Mark VII)")
        act_vision = menu.addAction("👁️‍🗨️ Multimodal Screen Vision")
        act_coder = menu.addAction("💻 Autonomous AI Coder (VS Code)")
        act_game = menu.addAction("🎮 Stark Repulsor Strike (Air-Game)")
        act_gaze = menu.addAction("👁️ Eye-Gaze Attention Lock")
        act_canvas = menu.addAction("🎨 Air-Canvas Laser Writer")
        act_gesture = menu.addAction("🖐️ Touchless Gestures")
        act_eye_mouse = menu.addAction("👁️ Cyber Ocular Eye-Mouse (Double-Blink)")
        act_shield = menu.addAction("🛡️ Shoulder-Surfer Privacy Shield")
        act_doc = menu.addAction("🩺 OS Doctor & RAM Boost")
        menu.addSeparator()

        act_close = menu.addAction("❌ Hide Arc Reactor Orb")

        chosen = menu.exec(pos)
        if chosen == act_voice:
            self.voice_toggled.emit()
        elif chosen == act_dashboard:
            self.open_dashboard.emit()
        elif chosen == act_hud:
            self.trigger_action.emit("HOLOGRAPHIC_HUD_ENGAGE")
        elif chosen == act_vision:
            self.trigger_action.emit("what is on my screen")
        elif chosen == act_coder:
            from PyQt6.QtWidgets import QInputDialog
            task, ok = QInputDialog.getText(
                None, "SHRIVA AI - Autonomous AI Coder",
                "What software, website, or script do you want Jarvis to code and open in VS Code?",
                text="Create a modern portfolio website with dark theme and glassmorphism"
            )
            if ok and task.strip():
                self.trigger_action.emit(task.strip())
        elif chosen == act_game:
            self.trigger_action.emit("REPULSOR_GAME_OPEN")
        elif chosen == act_gaze:
            self.trigger_action.emit("GAZE_TRACKER_START")
        elif chosen == act_canvas:
            self.trigger_action.emit("AIR_CANVAS_OPEN")
        elif chosen == act_gesture:
            self.trigger_action.emit("GESTURE_CONTROL_START")
        elif chosen == act_eye_mouse:
            self.trigger_action.emit("EYE_MOUSE_START")
        elif chosen == act_shield:
            self.trigger_action.emit("PRIVACY_SHIELD_START")
        elif chosen == act_doc:
            self.trigger_action.emit("OS_DOCTOR_RUN")
        elif chosen == act_close:
            self.close()

    # --- Iron Man Arc Reactor Paint Pipeline ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = 82.5
        cy = 75.0
        radius = 55.0

        # Pulse value (0.8 to 1.1)
        pulse = 0.95 + 0.15 * math.sin(self.pulse_phase)
        base_color = QColor(0, 240, 255) if not self.is_listening else QColor(0, 255, 140)

        # 1. Subtle Outer Ambient Glow
        ambient = QRadialGradient(cx, cy, radius * 1.3)
        ambient.setColorAt(0.0, QColor(base_color.red(), base_color.green(), base_color.blue(), int(45 * pulse)))
        ambient.setColorAt(0.8, QColor(base_color.red(), base_color.green(), base_color.blue(), int(15 * pulse)))
        ambient.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(ambient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPoint(int(cx), int(cy)), int(radius * 1.3), int(radius * 1.3))

        # 2. Dark Armor Chasis Ring
        painter.setBrush(QBrush(QColor(12, 18, 28, 225)))
        pen_chassis = QPen(QColor(30, 48, 70), 2.5)
        painter.setPen(pen_chassis)
        painter.drawEllipse(QPoint(int(cx), int(cy)), int(radius), int(radius))

        # 3. Outer Rotating Cyber Ring with Tick Marks
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.outer_angle)
        pen_tick = QPen(base_color, 1.5)
        painter.setPen(pen_tick)

        for i in range(16):
            angle = i * (360.0 / 16.0)
            rad = math.radians(angle)
            r_in = radius - (6.0 if i % 2 == 0 else 3.5)
            r_out = radius - 1.0
            x1 = r_in * math.cos(rad)
            y1 = r_in * math.sin(rad)
            x2 = r_out * math.cos(rad)
            y2 = r_out * math.sin(rad)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        painter.restore()

        # 4. Concentric Energy Wave Guide Ring
        pen_mid = QPen(QColor(base_color.red(), base_color.green(), base_color.blue(), 160), 2.0)
        painter.setPen(pen_mid)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPoint(int(cx), int(cy)), int(radius - 12), int(radius - 12))

        # 5. Inner Rotating 8-Coil Reactor Hub
        painter.save()
        painter.translate(cx, cy)
        painter.rotate(self.inner_angle)

        num_coils = 8
        coil_len = 8.0
        coil_r = radius - 20.0
        pen_coil = QPen(QColor(255, 255, 255, int(220 * pulse)), 2.8)
        painter.setPen(pen_coil)

        for i in range(num_coils):
            angle = i * (360.0 / num_coils)
            rad = math.radians(angle)
            x1 = (coil_r - coil_len) * math.cos(rad)
            y1 = (coil_r - coil_len) * math.sin(rad)
            x2 = coil_r * math.cos(rad)
            y2 = coil_r * math.sin(rad)
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        painter.restore()

        # 6. Center Palladium Power Core (Glowing Heart)
        core_grad = QRadialGradient(cx, cy, 18.0)
        core_grad.setColorAt(0.0, QColor(255, 255, 255, 255))
        core_grad.setColorAt(0.4, QColor(base_color.red(), base_color.green(), base_color.blue(), int(230 * pulse)))
        core_grad.setColorAt(1.0, QColor(base_color.red(), base_color.green(), base_color.blue(), 40))

        painter.setBrush(QBrush(core_grad))
        pen_core = QPen(QColor(255, 255, 255, 200), 1.5)
        painter.setPen(pen_core)
        painter.drawEllipse(QPoint(int(cx), int(cy)), 16, 16)

        # 7. Status HUD Text below Arc Reactor
        painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        pen_text = QPen(base_color)
        painter.setPen(pen_text)
        painter.drawText(0, 150, 165, 16, Qt.AlignmentFlag.AlignCenter, self.status_text)


active_arc_orb = None

def launch_arc_orb(parent=None):
    """Launches or brings to front the Iron Man Arc Reactor Desktop Orb."""
    global active_arc_orb
    if not active_arc_orb:
        active_arc_orb = ArcReactorOrb(parent=parent)
    active_arc_orb.show()
    active_arc_orb.raise_()
    active_arc_orb.activateWindow()
    return active_arc_orb

def close_arc_orb():
    """Hides the Arc Reactor Desktop Orb."""
    global active_arc_orb
    if active_arc_orb:
        active_arc_orb.close()
