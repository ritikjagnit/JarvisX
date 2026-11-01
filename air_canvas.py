import os
import sys
import time
import math
import cv2
import numpy as np
from datetime import datetime

from PyQt6.QtCore import QThread, pyqtSignal, Qt, QPoint, QRect
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QFont, QGuiApplication, QPainterPath, QImage, QBrush
)
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QApplication
)
from voice_engine import speak
from jarvis_sfx import play_sfx

DRAWINGS_DIR = os.path.join("jarvis_data", "air_canvas_drawings")


class AirCanvasTrackingThread(QThread):
    """
    Advanced Optical Fingertip Tracker.
    Features:
    1. Automatic Face Masking: Prevents user's face from contaminating hand detection.
    2. Broad YCrCb + HSV Multi-Lighting Skin Segmentation: Works in warm, cool, and dim rooms.
    3. Normalized Hand Geometry: Accurately identifies drawing finger at any distance from laptop.
    4. Real-time PIP HUD Camera Feed generation with cyber visual diagnostics.
    """
    # x, y, is_drawing, camera_thumb, status_text
    point_tracked = pyqtSignal(int, int, bool, QImage, str)

    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self.running = False
        self.force_always_draw = False  # When True, draws whenever hand is seen
        screen = QGuiApplication.primaryScreen()
        geom = screen.geometry() if screen else None
        self.screen_w = geom.width() if geom else 1920
        self.screen_h = geom.height() if geom else 1080

    def run(self):
        # Stop any other camera thread to avoid Windows DirectShow lock conflicts
        try:
            from eye_mouse import eye_mouse_controller
            if eye_mouse_controller.is_active:
                eye_mouse_controller.stop()
        except Exception:
            pass
        try:
            from air_gesture_controller import air_gesture_controller
            if air_gesture_controller.is_active:
                air_gesture_controller.stop()
        except Exception:
            pass
        try:
            from shoulder_surfer_shield import shield_controller
            if shield_controller.is_active:
                shield_controller.stop()
        except Exception:
            pass
        try:
            from gaze_tracker import stop_gaze_tracker
            stop_gaze_tracker()
        except Exception:
            pass

        self.running = True
        import face_recognition

        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(self.camera_index)

        if not cap.isOpened():
            print("[AIR-CANVAS ERROR] Camera unavailable.")
            dummy = np.zeros((120, 160, 3), dtype=np.uint8)
            cv2.putText(dummy, "CAM ERR", (30, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            qimg = QImage(dummy.data, 160, 120, 160 * 3, QImage.Format.Format_RGB888)
            self.point_tracked.emit(-1, -1, False, qimg, "CAMERA UNAVAILABLE")
            self.running = False
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

        margin_x = 40
        margin_y = 35
        prev_x, prev_y = self.screen_w // 2, self.screen_h // 2

        frame_idx = 0
        face_box = None  # (top, right, bottom, left)

        print("[AIR-CANVAS] Optical Hand & Fingertip Tracking Thread ONLINE.")

        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.015)
                continue

            frame_idx += 1
            frame = cv2.flip(frame, 1)  # Mirror so right movement is right
            h, w, _ = frame.shape

            # 1. Periodic Face Detection to eliminate Face-Skin contamination
            if frame_idx % 12 == 1:
                try:
                    small_rgb = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), (160, 120))
                    faces = face_recognition.face_locations(small_rgb)
                    if faces:
                        # Scale 160x120 back to 480x360 (ratio 3.0)
                        top, right, bottom, left = faces[0]
                        face_box = (int(top * 3.0), int(right * 3.0), int(bottom * 3.0), int(left * 3.0))
                    else:
                        face_box = None
                except Exception:
                    face_box = None

            # 2. Broad YCrCb + HSV Multi-Lighting Skin Segmentation
            ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
            mask_ycrcb = cv2.inRange(ycrcb, np.array([0, 128, 68]), np.array([255, 185, 135]))

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask_hsv = cv2.inRange(hsv, np.array([0, 25, 40]), np.array([28, 240, 255]))

            mask = cv2.bitwise_or(mask_ycrcb, mask_hsv)
            mask = cv2.GaussianBlur(mask, (5, 5), 0)

            # 3. Mask out Face & Neck if detected
            if face_box:
                t, r, b, l = face_box
                # Blackout from top of frame through neck
                cv2.rectangle(
                    mask,
                    (max(0, l - 35), 0),
                    (min(w, r + 35), min(h, b + 55)),
                    0,
                    -1
                )
                # Visual guide on debug preview
                cv2.rectangle(
                    frame,
                    (max(0, l - 35), 0),
                    (min(w, r + 35), min(h, b + 55)),
                    (60, 60, 60),
                    1
                )

            # 4. Find Hand Contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            target_point = None
            is_drawing = False
            status_text = "⚠️ NO HAND DETECTED"

            if contours and len(contours) > 0:
                # Find largest skin contour outside face
                max_cnt = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(max_cnt)

                if area > 800:
                    # Fingertip is the topmost point of the hand contour
                    topmost = tuple(max_cnt[max_cnt[:, :, 1].argmin()][0])
                    fx, fy = topmost

                    # Hand centroid
                    M = cv2.moments(max_cnt)
                    if M["m00"] > 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                    else:
                        cx, cy = fx, fy + 40

                    # Bounding box
                    bx, by, bw, bh = cv2.boundingRect(max_cnt)
                    vert_ext = cy - fy
                    vert_ratio = vert_ext / float(bh + 1e-5)

                    # Drawing vs Hovering decision:
                    if self.force_always_draw:
                        is_drawing = True
                        status_text = "✍️ DRAWING [ALWAYS-ON]"
                        draw_color = (0, 255, 136)
                    elif vert_ratio > 0.30 or vert_ext > 22:
                        # Pointing Index Finger
                        is_drawing = True
                        status_text = "✍️ DRAWING (Finger Point)"
                        draw_color = (0, 255, 136) # Neon Green
                    else:
                        # Lowered hand or open palm
                        is_drawing = False
                        status_text = "👁️ HOVERING (Move/Open Palm)"
                        draw_color = (255, 200, 0) # Cyan/Yellow

                    # Map coordinates to screen resolution
                    clamped_x = max(margin_x, min(w - margin_x, fx))
                    clamped_y = max(margin_y, min(h - margin_y, fy))

                    norm_x = (clamped_x - margin_x) / (w - 2 * margin_x)
                    norm_y = (clamped_y - margin_y) / (h - 2 * margin_y)

                    target_x = int(norm_x * self.screen_w)
                    target_y = int(norm_y * self.screen_h)

                    # Smooth interpolation
                    curr_x = int(prev_x + 0.42 * (target_x - prev_x))
                    curr_y = int(prev_y + 0.42 * (target_y - prev_y))
                    prev_x, prev_y = curr_x, curr_y
                    target_point = (curr_x, curr_y)

                    # Draw visual diagnostic markers on frame
                    cv2.drawContours(frame, [max_cnt], -1, draw_color, 1)
                    cv2.circle(frame, (fx, fy), 6, draw_color, -1)
                    cv2.circle(frame, (fx, fy), 12, draw_color, 1)
                    cv2.line(frame, (cx, cy), (fx, fy), (255, 255, 255), 1)

            # 5. Generate PIP Thumbnail (160x120) with cyber status
            thumb_bgr = cv2.resize(frame, (160, 120))
            thumb_rgb = cv2.cvtColor(thumb_bgr, cv2.COLOR_BGR2RGB)
            qimg = QImage(
                thumb_rgb.data,
                160,
                120,
                160 * 3,
                QImage.Format.Format_RGB888
            ).copy()

            if target_point:
                self.point_tracked.emit(target_point[0], target_point[1], is_drawing, qimg, status_text)
            else:
                self.point_tracked.emit(-1, -1, False, qimg, status_text)

            time.sleep(0.015)

        if cap and cap.isOpened():
            cap.release()
        print("[AIR-CANVAS] Optical Hand Tracking Thread OFFLINE.")

    def stop(self):
        self.running = False
        self.wait(1200)


class AirCanvasWindow(QDialog):
    """
    Transparent Holographic Mid-Air Laser Sketching Window.
    Features:
    - Glowing neon laser trails with dynamic outer bloom.
    - Live Cyber PIP Camera HUD in bottom-right corner.
    - Gesture Draw vs Always-Draw toggle (Spacebar).
    - Full color palette, eraser mode, clear, save PNG, and mouse fallback.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SHRIVA AI - AIR CANVAS LASER SKETCHER")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        screen = QGuiApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())

        # Strokes storage: list of (color, glow_color, is_eraser, list of QPoints)
        self.strokes = []
        self.current_stroke = []
        self.current_tip = None
        self.is_drawing_active = False

        # Mode & Colors
        self.is_eraser = False
        self.always_draw = False
        self.active_color = QColor(0, 240, 255, 245)     # Arc Reactor Cyan
        self.active_glow = QColor(0, 180, 255, 90)
        self.active_brush_size = 5

        # PIP Camera HUD state
        self.show_pip = True
        self.latest_thumb = None
        self.latest_status = "INITIALIZING SENSORS..."

        # Mouse drawing fallback state
        self.mouse_drawing = False

        # Start Camera Tracking Thread
        self.tracker = AirCanvasTrackingThread()
        self.tracker.point_tracked.connect(self._on_point_tracked)
        self.tracker.start()

        self._init_top_bar()
        play_sfx("ack")
        speak("Air Canvas Online. Point your index finger to sketch in the air.")

    def _init_top_bar(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)

        top_bar = QFrame()
        top_bar.setStyleSheet("""
            QFrame {
                background: rgba(10, 16, 30, 0.94);
                border: 1.5px solid #00f0ff;
                border-radius: 12px;
                padding: 6px 14px;
            }
            QLabel {
                color: #00f0ff;
                font-family: 'Consolas', 'Segoe UI', monospace;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton {
                background: rgba(0, 240, 255, 0.12);
                color: #ffffff;
                border: 1px solid #00f0ff;
                border-radius: 6px;
                padding: 5px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background: rgba(0, 240, 255, 0.40);
                color: #00ffff;
            }
            QPushButton#btn_green {
                border-color: #00ff88;
                color: #00ff88;
            }
            QPushButton#btn_red {
                border-color: #ff3366;
                color: #ff3366;
            }
            QPushButton#btn_gold {
                border-color: #ffcc00;
                color: #ffcc00;
            }
            QPushButton#btn_purple {
                border-color: #bf55ec;
                color: #bf55ec;
            }
            QPushButton#btn_mode {
                border-color: #38bdf8;
                color: #38bdf8;
            }
            QPushButton#btn_eraser {
                border-color: #f59e0b;
                color: #f59e0b;
            }
            QPushButton#btn_close {
                border-color: #ef4444;
                color: #ef4444;
            }
            QPushButton#btn_close:hover {
                background: rgba(239, 68, 68, 0.5);
                color: #ffffff;
            }
        """)

        bar_layout = QHBoxLayout(top_bar)
        title = QLabel("⚡ SHRIVA AI // AIR CANVAS LASER SKETCHER")
        bar_layout.addWidget(title)
        bar_layout.addSpacing(15)

        # Color Buttons
        btn_cyan = QPushButton("● CYAN")
        btn_cyan.clicked.connect(lambda: self.set_color(QColor(0, 240, 255, 245), QColor(0, 180, 255, 90)))
        bar_layout.addWidget(btn_cyan)

        btn_green = QPushButton("● GREEN")
        btn_green.setObjectName("btn_green")
        btn_green.clicked.connect(lambda: self.set_color(QColor(0, 255, 136, 245), QColor(0, 220, 100, 90)))
        bar_layout.addWidget(btn_green)

        btn_red = QPushButton("● STARK RED")
        btn_red.setObjectName("btn_red")
        btn_red.clicked.connect(lambda: self.set_color(QColor(255, 51, 102, 245), QColor(255, 0, 80, 90)))
        bar_layout.addWidget(btn_red)

        btn_gold = QPushButton("● GOLD")
        btn_gold.setObjectName("btn_gold")
        btn_gold.clicked.connect(lambda: self.set_color(QColor(255, 204, 0, 245), QColor(255, 160, 0, 90)))
        bar_layout.addWidget(btn_gold)

        btn_purple = QPushButton("● PURPLE")
        btn_purple.setObjectName("btn_purple")
        btn_purple.clicked.connect(lambda: self.set_color(QColor(191, 85, 236, 245), QColor(160, 50, 220, 90)))
        bar_layout.addWidget(btn_purple)

        bar_layout.addSpacing(10)

        # Draw Mode Toggle (Gesture vs Always Draw)
        self.btn_mode = QPushButton("☝️ GESTURE DRAW [SPACE]")
        self.btn_mode.setObjectName("btn_mode")
        self.btn_mode.clicked.connect(self.toggle_draw_mode)
        bar_layout.addWidget(self.btn_mode)

        # Eraser Toggle
        self.btn_eraser = QPushButton("🧽 ERASER [E]")
        self.btn_eraser.setObjectName("btn_eraser")
        self.btn_eraser.clicked.connect(self.toggle_eraser)
        bar_layout.addWidget(self.btn_eraser)

        # Clear Canvas
        clear_btn = QPushButton("🧹 CLEAR [C]")
        clear_btn.clicked.connect(self.clear_canvas)
        bar_layout.addWidget(clear_btn)

        # Save Canvas
        save_btn = QPushButton("💾 SAVE [S]")
        save_btn.clicked.connect(self.save_canvas)
        bar_layout.addWidget(save_btn)

        # Toggle PIP Camera
        self.btn_pip = QPushButton("📷 HUD PIP [H]")
        self.btn_pip.clicked.connect(self.toggle_pip)
        bar_layout.addWidget(self.btn_pip)

        bar_layout.addStretch()

        close_btn = QPushButton("✕ EXIT")
        close_btn.setObjectName("btn_close")
        close_btn.clicked.connect(self.close)
        bar_layout.addWidget(close_btn)

        layout.addWidget(top_bar, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addStretch()

    def set_color(self, core_color, glow_color):
        self.is_eraser = False
        self.btn_eraser.setText("🧽 ERASER [E]")
        self.active_color = core_color
        self.active_glow = glow_color

    def toggle_draw_mode(self):
        self.always_draw = not self.always_draw
        if self.tracker:
            self.tracker.force_always_draw = self.always_draw
        if self.always_draw:
            self.btn_mode.setText("✏️ ALWAYS DRAW [SPACE]")
            self.btn_mode.setStyleSheet("border-color: #00ff88; color: #00ff88;")
        else:
            self.btn_mode.setText("☝️ GESTURE DRAW [SPACE]")
            self.btn_mode.setStyleSheet("")

    def toggle_eraser(self):
        self.is_eraser = not self.is_eraser
        if self.is_eraser:
            self.btn_eraser.setText("✏️ PEN MODE [E]")
        else:
            self.btn_eraser.setText("🧽 ERASER [E]")

    def toggle_pip(self):
        self.show_pip = not self.show_pip
        self.update()

    def _on_point_tracked(self, x, y, is_drawing, thumb, status):
        self.latest_thumb = thumb
        self.latest_status = status

        if x >= 0 and y >= 0:
            pt = QPoint(x, y)
            self.current_tip = pt
            self.is_drawing_active = is_drawing

            if is_drawing:
                self.current_stroke.append(pt)
            else:
                if self.current_stroke:
                    self.strokes.append((
                        self.active_color,
                        self.active_glow,
                        self.is_eraser,
                        list(self.current_stroke)
                    ))
                    self.current_stroke.clear()
        else:
            self.current_tip = None
            self.is_drawing_active = False
            if self.current_stroke:
                self.strokes.append((
                    self.active_color,
                    self.active_glow,
                    self.is_eraser,
                    list(self.current_stroke)
                ))
                self.current_stroke.clear()

        self.update()

    # Mouse drawing fallback
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.mouse_drawing = True
            self.current_stroke.append(event.pos())
            self.update()

    def mouseMoveEvent(self, event):
        if self.mouse_drawing:
            self.current_stroke.append(event.pos())
            self.current_tip = event.pos()
            self.is_drawing_active = True
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.mouse_drawing:
            self.mouse_drawing = False
            if self.current_stroke:
                self.strokes.append((
                    self.active_color,
                    self.active_glow,
                    self.is_eraser,
                    list(self.current_stroke)
                ))
                self.current_stroke.clear()
            self.is_drawing_active = False
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Subtle Cyber Backdrop (semi-translucent dark slate)
        painter.fillRect(self.rect(), QColor(5, 10, 22, 130))

        # 2. Render all past strokes
        def _draw_stroke(core_col, glow_col, is_erase, pts):
            if len(pts) < 2:
                return
            path = QPainterPath()
            path.moveTo(pts[0])
            for p in pts[1:]:
                path.lineTo(p)

            if is_erase:
                # Eraser: cuts through canvas with background shade
                pen_erase = QPen(QColor(5, 10, 22, 255), 24, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen_erase)
                painter.drawPath(path)
            else:
                # Outer Glow Bloom
                pen_glow = QPen(glow_col, 14, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen_glow)
                painter.drawPath(path)

                # Core Bright Laser Line
                pen_core = QPen(core_col, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
                painter.setPen(pen_core)
                painter.drawPath(path)

        for col, glow, is_erase, stroke in self.strokes:
            _draw_stroke(col, glow, is_erase, stroke)

        # 3. Render active drawing stroke
        if self.current_stroke:
            _draw_stroke(self.active_color, self.active_glow, self.is_eraser, self.current_stroke)

        # 4. Laser Reticle following fingertip
        if self.current_tip:
            tx = self.current_tip.x()
            ty = self.current_tip.y()
            ret_col = QColor(245, 158, 11) if self.is_eraser else (
                QColor(0, 255, 136) if self.is_drawing_active else self.active_color
            )

            # Outer ring
            painter.setPen(QPen(ret_col, 1.5))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(self.current_tip, 16, 16)

            # Inner pulsing dot
            painter.setBrush(QBrush(QColor(ret_col.red(), ret_col.green(), ret_col.blue(), 180)))
            painter.drawEllipse(self.current_tip, 5, 5)

            # Laser Crosshairs
            painter.setPen(QPen(ret_col, 1, Qt.PenStyle.DashLine))
            painter.drawLine(tx - 24, ty, tx - 18, ty)
            painter.drawLine(tx + 18, ty, tx + 24, ty)
            painter.drawLine(tx, ty - 24, tx, ty - 18)
            painter.drawLine(tx, ty + 18, tx, ty + 24)

        # 5. PIP Live Camera HUD Box (Bottom-Right Corner)
        if self.show_pip and self.latest_thumb:
            pw, ph = 180, 135
            px = self.width() - pw - 25
            py = self.height() - ph - 25

            # Backdrop
            painter.setPen(QPen(QColor(0, 240, 255, 180), 1.5))
            painter.setBrush(QColor(10, 16, 30, 230))
            painter.drawRoundedRect(px, py, pw, ph, 8, 8)

            # Live Thumbnail Image
            thumb_rect = QRect(px + 10, py + 10, 160, 95)
            painter.drawImage(thumb_rect, self.latest_thumb)

            # Status Badge
            badge_color = QColor(0, 255, 136) if "DRAWING" in self.latest_status else (
                QColor(0, 240, 255) if "HOVERING" in self.latest_status else QColor(245, 158, 11)
            )
            painter.setPen(badge_color)
            painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
            painter.drawText(px + 10, py + 122, self.latest_status)

    def clear_canvas(self):
        self.strokes.clear()
        self.current_stroke.clear()
        self.update()
        play_sfx("ack")

    def save_canvas(self):
        os.makedirs(DRAWINGS_DIR, exist_ok=True)
        fname = f"shriva_air_sketch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        fpath = os.path.join(DRAWINGS_DIR, fname)
        pix = self.grab()
        pix.save(fpath, "PNG")
        play_sfx("ack")
        speak("Air Canvas drawing saved successfully to your gallery.")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Space:
            self.toggle_draw_mode()
        elif event.key() == Qt.Key.Key_C:
            self.clear_canvas()
        elif event.key() == Qt.Key.Key_S:
            self.save_canvas()
        elif event.key() == Qt.Key.Key_E:
            self.toggle_eraser()
        elif event.key() == Qt.Key.Key_H:
            self.toggle_pip()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        global active_canvas_window
        if self.tracker:
            self.tracker.stop()
        active_canvas_window = None
        super().closeEvent(event)


# Global instances for standalone / bridge usage
active_canvas_window = None

def launch_canvas_window():
    global active_canvas_window
    if active_canvas_window:
        try:
            active_canvas_window.close()
        except Exception:
            pass
        active_canvas_window = None

    active_canvas_window = AirCanvasWindow()
    active_canvas_window.showFullScreen()
    active_canvas_window.raise_()
    active_canvas_window.activateWindow()
    return active_canvas_window

def close_canvas_window():
    global active_canvas_window
    if active_canvas_window:
        active_canvas_window.close()
        active_canvas_window = None
