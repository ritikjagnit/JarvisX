import os
import sys
import time
import math
import json
import random
import cv2
import numpy as np

from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPointF, QRectF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QRadialGradient, QLinearGradient,
    QImage, QPixmap, QKeySequence, QShortcut, QPainterPath
)
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QApplication, QFrame
)

from jarvis_sfx import play_sfx
from voice_engine import speak

SCORES_FILE = os.path.join(os.path.dirname(__file__), "jarvis_data", "game_scores.json")

def load_high_score():
    if os.path.exists(SCORES_FILE):
        try:
            with open(SCORES_FILE, "r") as f:
                return json.load(f).get("high_score", 0)
        except Exception:
            return 0
    return 0

def save_high_score(score):
    os.makedirs(os.path.dirname(SCORES_FILE), exist_ok=True)
    current = load_high_score()
    if score > current:
        try:
            with open(SCORES_FILE, "w") as f:
                json.dump({"high_score": score, "date": time.strftime("%Y-%m-%d %H:%M")}, f)
        except Exception:
            pass
        return True
    return False


# =====================================================================
# Optical Hand Tracking Worker Thread (DirectShow + YCrCb)
# =====================================================================
class GameTrackingWorker(QThread):
    hand_updated = pyqtSignal(float, float, bool, QImage) # norm_x, norm_y, is_blasting, camera_thumb

    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self.running = False

    def run(self):
        self.running = True
        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(self.camera_index)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

        prev_x, prev_y = 0.5, 0.5
        prev_area = 0

        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.02)
                continue

            frame = cv2.flip(frame, 1) # Mirror
            h, w, _ = frame.shape

            ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
            mask = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))
            mask = cv2.GaussianBlur(mask, (5, 5), 0)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            norm_x, norm_y = prev_x, prev_y
            is_blasting = False

            if contours and len(contours) > 0:
                max_cnt = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(max_cnt)

                if area > 1800:
                    # Centroid & topmost point
                    M = cv2.moments(max_cnt)
                    if M["m00"] > 0:
                        cx = M["m10"] / M["m00"]
                        cy = M["m01"] / M["m00"]
                    else:
                        cx, cy = w // 2, h // 2

                    topmost = tuple(max_cnt[max_cnt[:, :, 1].argmin()][0])
                    # Weight towards fingertip/palm top
                    fx = cx * 0.4 + topmost[0] * 0.6
                    fy = cy * 0.4 + topmost[1] * 0.6

                    margin_x = 30
                    margin_y = 25
                    clamped_x = max(margin_x, min(w - margin_x, fx))
                    clamped_y = max(margin_y, min(h - margin_y, fy))

                    raw_nx = (clamped_x - margin_x) / (w - 2 * margin_x)
                    raw_ny = (clamped_y - margin_y) / (h - 2 * margin_y)

                    # Smooth EMA
                    norm_x = prev_x + 0.42 * (raw_nx - prev_x)
                    norm_y = prev_y + 0.42 * (raw_ny - prev_y)
                    prev_x, prev_y = norm_x, norm_y

                    # Detect rapid area expansion or open palm for gesture firing
                    if area > prev_area * 1.35 and area > 6000:
                        is_blasting = True
                    prev_area = area

                    # Draw tracker HUD overlay on thumbnail
                    cv2.circle(frame, (int(fx), int(fy)), 14, (0, 255, 255), 2)
                    cv2.circle(frame, (int(fx), int(fy)), 4, (0, 255, 0), -1)

            # Convert frame to QImage for live thumbnail HUD in game
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            bytes_per_line = 3 * w
            thumb_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()

            self.hand_updated.emit(norm_x, norm_y, is_blasting, thumb_img)
            time.sleep(0.02) # ~45 FPS

        cap.release()

    def stop(self):
        self.running = False
        self.wait(800)


# =====================================================================
# Target / Particle Data Models
# =====================================================================
class Target:
    def __init__(self, t_type, x, y, vx, vy, size):
        self.t_type = t_type # 'drone', 'missile', 'plasma', 'time_boost'
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.alive = True
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-4, 4)
        self.dwell_time = 0.0 # Time player has hovered over this target

class Particle:
    def __init__(self, x, y, color, speed_mult=1.0):
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 10) * speed_mult
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.life = 1.0 # 1.0 down to 0.0
        self.decay = random.uniform(0.04, 0.08)
        self.size = random.uniform(3, 7)

class FloatingText:
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.life = 1.0
        self.vy = -2.0

class RepulsorBeam:
    def __init__(self, start_x, start_y, target_x, target_y):
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.life = 1.0 # decays rapidly over ~150ms


# =====================================================================
# MAIN STARK REPULSOR STRIKE GAME WINDOW
# =====================================================================
class StarkRepulsorGame(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SHRIVA AI: STARK REPULSOR STRIKE")
        self.resize(1180, 720)
        self.setMinimumSize(960, 600)
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)

        # Center on primary screen
        screen = QApplication.primaryScreen()
        if screen:
            geom = screen.availableGeometry()
            self.move((geom.width() - 1180) // 2, (geom.height() - 720) // 2)

        # Game State
        self.state = "START" # "START", "PLAYING", "GAMEOVER"
        self.score = 0
        self.high_score = load_high_score()
        self.combo = 1
        self.last_hit_time = 0.0
        self.time_left = 60.0
        self.shots_fired = 0
        self.shots_hit = 0

        # Entities
        self.targets = []
        self.particles = []
        self.floating_texts = []
        self.beams = []

        # Aim Reticle Position
        self.reticle_x = 590.0
        self.reticle_y = 360.0
        self.reticle_angle = 0.0
        self.reticle_locked = False
        self.camera_thumb = None

        # Stars in background
        self.stars = [
            (random.uniform(0, 1920), random.uniform(0, 1080), random.uniform(1, 2.5), random.uniform(0.3, 0.9))
            for _ in range(60)
        ]

        # Shortcuts
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self, self.close)
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self.fire_repulsor_blast)

        # Camera Worker Thread
        self.worker = GameTrackingWorker(camera_index=0, parent=self)
        self.worker.hand_updated.connect(self._on_hand_update)
        self.worker.start()

        # 60 FPS Game Loop Timer
        self.game_timer = QTimer(self)
        self.game_timer.timeout.connect(self._game_loop)
        self.game_timer.start(16) # ~60 FPS

        # Target Spawner Timer
        self.spawn_timer = QTimer(self)
        self.spawn_timer.timeout.connect(self._spawn_target)

        # Play Entrance Chime
        play_sfx("boot")

    def _on_hand_update(self, norm_x, norm_y, is_blasting, thumb_img):
        w = self.width()
        h = self.height()
        target_x = norm_x * w
        target_y = norm_y * h

        # Smooth reticle movement
        self.reticle_x += 0.45 * (target_x - self.reticle_x)
        self.reticle_y += 0.45 * (target_y - self.reticle_y)
        self.camera_thumb = thumb_img

        if is_blasting and self.state == "PLAYING":
            self.fire_repulsor_blast()

    def start_game(self):
        self.state = "PLAYING"
        self.score = 0
        self.combo = 1
        self.last_hit_time = time.time()
        self.time_left = 60.0
        self.shots_fired = 0
        self.shots_hit = 0
        self.targets.clear()
        self.particles.clear()
        self.floating_texts.clear()
        self.beams.clear()

        self.spawn_timer.start(950)
        play_sfx("ack")
        speak("Repulsor combat protocol engaged. Fire at will, Sir.")

    def end_game(self):
        self.state = "GAMEOVER"
        self.spawn_timer.stop()
        is_new_high = save_high_score(self.score)
        self.high_score = load_high_score()

        accuracy = int((self.shots_hit / max(1, self.shots_fired)) * 100)
        play_sfx("success")

        if is_new_high:
            speak(f"Spectacular marksmanship, Sir! New record score: {self.score} points with {accuracy} percent accuracy.")
        else:
            speak(f"Training simulation concluded. Final score: {self.score} points.")

    def _spawn_target(self):
        if self.state != "PLAYING":
            return

        w = self.width()
        h = self.height()
        side = random.choice(["left", "right", "top"])

        # Decide type
        rand_val = random.random()
        if rand_val < 0.60:
            t_type = "drone"
            size = 38
            speed = random.uniform(2.5, 4.5)
        elif rand_val < 0.85:
            t_type = "missile"
            size = 28
            speed = random.uniform(5.0, 7.5)
        elif rand_val < 0.94:
            t_type = "plasma"
            size = 46
            speed = random.uniform(1.8, 3.0)
        else:
            t_type = "time_boost"
            size = 34
            speed = random.uniform(2.2, 3.8)

        if side == "left":
            x = -size
            y = random.uniform(80, h - 160)
            vx = speed
            vy = random.uniform(-1.2, 1.2)
        elif side == "right":
            x = w + size
            y = random.uniform(80, h - 160)
            vx = -speed
            vy = random.uniform(-1.2, 1.2)
        else:
            x = random.uniform(80, w - 80)
            y = -size
            vx = random.uniform(-2, 2)
            vy = speed * 0.8

        self.targets.append(Target(t_type, x, y, vx, vy, size))

    def fire_repulsor_blast(self):
        if self.state != "PLAYING":
            return

        self.shots_fired += 1
        play_sfx("blast")

        # Beam originates from bottom center (repulsor gauntlet) to reticle
        rx = self.reticle_x
        ry = self.reticle_y
        self.beams.append(RepulsorBeam(self.width() / 2, self.height() + 20, rx, ry))

        # Check hits
        hit_any = False
        for t in self.targets:
            if not t.alive:
                continue
            dist = math.hypot(rx - t.x, ry - t.y)
            if dist < t.size * 1.35:
                self._destroy_target(t)
                hit_any = True
                break

        if not hit_any:
            # Combo resets on miss if no hit in 2 seconds
            if time.time() - self.last_hit_time > 2.0:
                self.combo = 1

    def _destroy_target(self, target):
        target.alive = False
        self.shots_hit += 1
        now = time.time()

        # Update Combo
        if now - self.last_hit_time < 1.8:
            self.combo = min(self.combo + 1, 5)
        else:
            self.combo = 1
        self.last_hit_time = now

        # Points
        base_points = {
            "drone": 100,
            "missile": 250,
            "plasma": 500,
            "time_boost": 150
        }.get(target.t_type, 100)

        points = base_points * self.combo
        self.score += points

        # Play explosion SFX
        play_sfx("explosion")

        # Spawn particle explosion
        col = {
            "drone": QColor(255, 60, 60),
            "missile": QColor(255, 170, 0),
            "plasma": QColor(0, 240, 255),
            "time_boost": QColor(0, 255, 130)
        }.get(target.t_type, QColor(0, 255, 255))

        for _ in range(24):
            self.particles.append(Particle(target.x, target.y, col))

        # Floating score text
        combo_str = f" (x{self.combo}!)" if self.combo > 1 else ""
        self.floating_texts.append(FloatingText(f"+{points}{combo_str}", target.x, target.y - 15, col))

        # Special Abilities
        if target.t_type == "plasma":
            # EMP Shockwave clears ALL targets!
            for other in self.targets:
                if other.alive:
                    other.alive = False
                    self.score += 75
                    for _ in range(8):
                        self.particles.append(Particle(other.x, other.y, QColor(0, 240, 255)))
            self.floating_texts.append(FloatingText("⚡ EMP SHOCKWAVE WIPEOUT!", self.width() / 2, self.height() / 2, QColor(0, 255, 255)))

        elif target.t_type == "time_boost":
            self.time_left += 10.0
            self.floating_texts.append(FloatingText("⏱️ +10 SECONDS!", target.x, target.y - 35, QColor(0, 255, 130)))

    # --- Mouse Controls Fallback ---
    def mouseMoveEvent(self, event):
        self.reticle_x = event.position().x()
        self.reticle_y = event.position().y()

    def mousePressEvent(self, event):
        if self.state == "START":
            self.start_game()
        elif self.state == "GAMEOVER":
            self.start_game()
        elif self.state == "PLAYING":
            self.fire_repulsor_blast()

    # --- 60 FPS Game Loop Update ---
    def _game_loop(self):
        dt = 0.016
        self.reticle_angle = (self.reticle_angle + 2.5) % 360.0

        if self.state == "PLAYING":
            self.time_left -= dt
            if self.time_left <= 0:
                self.time_left = 0
                self.end_game()

            # Target update & dwell lock-on check
            w = self.width()
            h = self.height()
            self.reticle_locked = False

            for t in self.targets:
                if not t.alive:
                    continue
                t.x += t.vx
                t.y += t.vy
                t.angle = (t.angle + t.spin) % 360.0

                # Check if reticle is hovering over target (Dwell Auto-Lock)
                dist = math.hypot(self.reticle_x - t.x, self.reticle_y - t.y)
                if dist < t.size * 1.3:
                    self.reticle_locked = True
                    t.dwell_time += dt

                    # If locked for >0.30s -> Auto Repulsor Blast!
                    if t.dwell_time >= 0.30:
                        self.fire_repulsor_blast()
                        break
                else:
                    t.dwell_time = max(0.0, t.dwell_time - dt * 2)

                # Despawn offscreen
                if t.x < -100 or t.x > w + 100 or t.y < -100 or t.y > h + 100:
                    t.alive = False

            self.targets = [t for t in self.targets if t.alive]

            # Combo decay if idle for >2.8s
            if time.time() - self.last_hit_time > 2.8:
                self.combo = 1

        # Beams update
        for b in self.beams:
            b.life -= dt * 6.5
        self.beams = [b for b in self.beams if b.life > 0]

        # Particles update
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.vy += 0.25 # Gravity
            p.life -= p.decay
        self.particles = [p for p in self.particles if p.life > 0]

        # Floating text update
        for ft in self.floating_texts:
            ft.y += ft.vy
            ft.life -= dt * 1.2
        self.floating_texts = [ft for ft in self.floating_texts if ft.life > 0]

        self.update()

    # --- Paint Pipeline ---
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # 1. Dark Space Background with Radial Vignette
        grad = QRadialGradient(w / 2, h / 2, max(w, h) * 0.7)
        grad.setColorAt(0.0, QColor(10, 18, 32))
        grad.setColorAt(0.7, QColor(4, 8, 16))
        grad.setColorAt(1.0, QColor(1, 3, 8))
        painter.fillRect(0, 0, w, h, grad)

        # 2. Twinkling Stars
        for sx, sy, s_size, s_alpha in self.stars:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(200, 230, 255, int(s_alpha * 200)))
            painter.drawEllipse(QPointF(sx % w, sy % h), s_size, s_size)

        # 3. Cyber Matrix Grid Lines
        painter.setPen(QPen(QColor(0, 240, 255, 18), 1, Qt.PenStyle.DashLine))
        grid_step = 60
        for gx in range(0, w, grid_step):
            painter.drawLine(gx, 0, gx, h)
        for gy in range(0, h, grid_step):
            painter.drawLine(0, gy, w, gy)

        # 4. Render Active Targets
        for t in self.targets:
            if not t.alive:
                continue
            self._draw_target(painter, t)

        # 5. Render Repulsor Laser Beams
        for b in self.beams:
            alpha = int(b.life * 255)
            # Core beam
            pen_core = QPen(QColor(255, 255, 255, alpha), 5)
            painter.setPen(pen_core)
            painter.drawLine(int(b.start_x), int(b.start_y), int(b.target_x), int(b.target_y))
            # Outer bloom
            pen_glow = QPen(QColor(0, 240, 255, int(alpha * 0.5)), 18)
            painter.setPen(pen_glow)
            painter.drawLine(int(b.start_x), int(b.start_y), int(b.target_x), int(b.target_y))

        # 6. Render Particles
        for p in self.particles:
            alpha = int(max(0.0, min(1.0, p.life)) * 255)
            p_col = QColor(p.color.red(), p.color.green(), p.color.blue(), alpha)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(p_col)
            painter.drawEllipse(QPointF(p.x, p.y), p.size * p.life, p.size * p.life)

        # 7. Render Floating Text
        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        for ft in self.floating_texts:
            alpha = int(max(0.0, min(1.0, ft.life)) * 255)
            t_col = QColor(ft.color.red(), ft.color.green(), ft.color.blue(), alpha)
            painter.setPen(t_col)
            painter.drawText(int(ft.x - 70), int(ft.y), 200, 25, Qt.AlignmentFlag.AlignCenter, ft.text)

        # 8. Render Iron Man Arc Reactor Aim Reticle
        self._draw_reticle(painter)

        # 9. Top Cyber HUD Bar
        self._draw_hud_bar(painter)

        # 10. Live Camera Thumbnail in Bottom-Left Corner
        self._draw_camera_thumbnail(painter)

        # 11. Overlays for START / GAMEOVER screens
        if self.state == "START":
            self._draw_start_screen(painter)
        elif self.state == "GAMEOVER":
            self._draw_gameover_screen(painter)

    # --- Draw Target Entities ---
    def _draw_target(self, painter, t):
        painter.save()
        painter.translate(t.x, t.y)
        painter.rotate(t.angle)

        s = t.size

        if t.t_type == "drone":
            # Red Ultron Sentry Drone
            painter.setBrush(QColor(30, 20, 25, 230))
            painter.setPen(QPen(QColor(255, 50, 70), 2))
            painter.drawRect(int(-s/2), int(-s/2), int(s), int(s))

            # Rotor blades
            painter.setPen(QPen(QColor(255, 120, 120, 180), 2))
            painter.drawLine(int(-s*0.8), int(-s*0.8), int(s*0.8), int(s*0.8))
            painter.drawLine(int(-s*0.8), int(s*0.8), int(s*0.8), int(-s*0.8))

            # Red Eye Core
            painter.setBrush(QColor(255, 0, 50))
            painter.drawEllipse(QPointF(0, 0), 6, 6)

        elif t.t_type == "missile":
            # Amber Rogue Missile
            painter.setBrush(QColor(40, 25, 10, 240))
            painter.setPen(QPen(QColor(255, 170, 0), 2))
            # Triangular dart shape
            poly = [QPointF(s * 0.9, 0), QPointF(-s * 0.7, -s * 0.45), QPointF(-s * 0.4, 0), QPointF(-s * 0.7, s * 0.45)]
            painter.drawPolygon(poly)

            # Flame thruster
            painter.setPen(QPen(QColor(255, 240, 100), 2))
            painter.drawLine(int(-s * 0.7), 0, int(-s * 1.3), 0)

        elif t.t_type == "plasma":
            # Cyan Glowing Plasma Core
            grad = QRadialGradient(0, 0, s)
            grad.setColorAt(0.0, QColor(255, 255, 255))
            grad.setColorAt(0.4, QColor(0, 240, 255, 220))
            grad.setColorAt(1.0, QColor(0, 120, 255, 40))
            painter.setBrush(grad)
            painter.setPen(QPen(QColor(0, 255, 255), 2))
            painter.drawEllipse(QPointF(0, 0), s, s)

            # Energy rings
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(255, 255, 255, 180), 1.5, Qt.PenStyle.DashLine))
            painter.drawEllipse(QPointF(0, 0), s * 0.6, s * 0.6)

        elif t.t_type == "time_boost":
            # Green Arc Reactor Token (+10s)
            painter.setBrush(QColor(10, 35, 20, 230))
            painter.setPen(QPen(QColor(0, 255, 140), 2.5))
            painter.drawEllipse(QPointF(0, 0), s, s)

            painter.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
            painter.setPen(QColor(0, 255, 140))
            painter.drawText(int(-s), int(-s), int(s * 2), int(s * 2), Qt.AlignmentFlag.AlignCenter, "+10s")

        # Draw lock-on charging progress arc if player is hovering
        if t.dwell_time > 0:
            prog = min(1.0, t.dwell_time / 0.30)
            span_angle = int(prog * 360 * 16)
            painter.setPen(QPen(QColor(255, 230, 0), 3))
            painter.drawArc(int(-s * 1.4), int(-s * 1.4), int(s * 2.8), int(s * 2.8), 90 * 16, -span_angle)

        painter.restore()

    # --- Draw Iron Man Reticle ---
    def _draw_reticle(self, painter):
        rx = self.reticle_x
        ry = self.reticle_y
        color = QColor(255, 50, 70) if self.reticle_locked else QColor(0, 240, 255)

        painter.save()
        painter.translate(rx, ry)

        # Concentric rotating rings
        painter.rotate(self.reticle_angle)
        pen_ring = QPen(color, 2)
        painter.setPen(pen_ring)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(0, 0), 32, 32)

        # 4 HUD Corner Brackets
        brk_len = 8
        for angle in [45, 135, 225, 315]:
            rad = math.radians(angle)
            bx = 42 * math.cos(rad)
            by = 42 * math.sin(rad)
            painter.drawLine(int(bx - brk_len), int(by), int(bx + brk_len), int(by))
            painter.drawLine(int(bx), int(by - brk_len), int(bx), int(by + brk_len))

        painter.rotate(-self.reticle_angle * 2)
        painter.setPen(QPen(color, 1.5, Qt.PenStyle.DotLine))
        painter.drawEllipse(QPointF(0, 0), 20, 20)

        # Center Crosshair Dot
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(QPointF(0, 0), 4, 4)

        # Lock text
        if self.reticle_locked:
            painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
            painter.setPen(QColor(255, 50, 70))
            painter.drawText(-50, 48, 100, 16, Qt.AlignmentFlag.AlignCenter, "[ TARGET LOCKED ]")

        painter.restore()

    # --- Draw Top HUD Bar ---
    def _draw_hud_bar(self, painter):
        w = self.width()

        # Top Bar Background
        painter.fillRect(0, 0, w, 55, QColor(8, 14, 24, 220))
        painter.setPen(QPen(QColor(0, 240, 255, 100), 1.5))
        painter.drawLine(0, 55, w, 55)

        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))

        # Title
        painter.setPen(QColor(0, 240, 255))
        painter.drawText(25, 34, "SHRIVA AI // STARK REPULSOR STRIKE")

        # Score & High Score
        painter.setPen(QColor(255, 255, 255))
        score_txt = f"SCORE: {self.score:,}   |   RECORD: {self.high_score:,}"
        painter.drawText(360, 34, score_txt)

        # Combo
        combo_col = QColor(255, 200, 0) if self.combo > 1 else QColor(140, 170, 200)
        painter.setPen(combo_col)
        painter.drawText(w - 380, 34, f"COMBO: x{self.combo}")

        # Timer
        time_col = QColor(255, 60, 60) if self.time_left < 10 else QColor(0, 255, 140)
        painter.setPen(time_col)
        painter.drawText(w - 230, 34, f"TIME: {int(self.time_left)}s")

        # Exit hint
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QColor(140, 160, 180))
        painter.drawText(w - 95, 34, "[ESC EXIT]")

    # --- Draw Live Camera Thumbnail in Bottom Corner ---
    def _draw_camera_thumbnail(self, painter):
        if not self.camera_thumb:
            return

        tw, th = 160, 120
        tx = 25
        ty = self.height() - th - 25

        # Border Card
        painter.fillRect(tx, ty, tw, th, QColor(10, 16, 26, 230))
        painter.setPen(QPen(QColor(0, 240, 255, 140), 1.5))
        painter.drawRect(tx, ty, tw, th)

        # Scaled Pixmap
        pix = QPixmap.fromImage(self.camera_thumb).scaled(tw - 4, th - 4, Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        painter.drawPixmap(tx + 2, ty + 2, pix)

        # Overlay text
        painter.setFont(QFont("Consolas", 7, QFont.Weight.Bold))
        painter.fillRect(tx + 2, ty + th - 18, tw - 4, 16, QColor(0, 0, 0, 180))
        painter.setPen(QColor(0, 255, 140))
        painter.drawText(tx + 6, ty + th - 6, "● WEBCAM VISION TRACKER")

    # --- Start Screen Overlay ---
    def _draw_start_screen(self, painter):
        w = self.width()
        h = self.height()

        painter.fillRect(0, 0, w, h, QColor(4, 8, 16, 215))

        # Title
        painter.setFont(QFont("Consolas", 32, QFont.Weight.Bold))
        painter.setPen(QColor(0, 240, 255))
        painter.drawText(0, h // 2 - 140, w, 50, Qt.AlignmentFlag.AlignCenter, "⚡ STARK REPULSOR STRIKE ⚡")

        painter.setFont(QFont("Segoe UI", 14))
        painter.setPen(QColor(220, 235, 255))
        painter.drawText(0, h // 2 - 75, w, 30, Qt.AlignmentFlag.AlignCenter, "Touchless Optical Air-Gesture Combat Simulator")

        # Instructions
        painter.setFont(QFont("Consolas", 11))
        painter.setPen(QColor(140, 200, 255))
        instructions = (
            "🖐️ Wave your hand in front of webcam to aim crosshair\n"
            "🎯 Hover over targets for 0.3s or Open Palm / Spacebar / Click to Fire\n"
            "💥 Ultron Drones (+100)  |  Missiles (+250)  |  Plasma EMP Core (+500 Wipe)\n"
            "⏱️ 60-Second Challenge  |  Build Combos for x5 Multiplier!"
        )
        painter.drawText(0, h // 2 - 25, w, 110, Qt.AlignmentFlag.AlignCenter, instructions)

        # Pulse Start Button
        btn_w, btn_h = 280, 50
        bx = (w - btn_w) // 2
        by = h // 2 + 105
        painter.setBrush(QColor(0, 240, 255, 45))
        painter.setPen(QPen(QColor(0, 240, 255), 2.5))
        painter.drawRoundedRect(bx, by, btn_w, btn_h, 12, 12)

        painter.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        painter.setPen(QColor(0, 255, 255))
        painter.drawText(bx, by + 32, btn_w, 30, Qt.AlignmentFlag.AlignHCenter, "[ CLICK TO LAUNCH MISSION ]")

    # --- Game Over Screen Overlay ---
    def _draw_gameover_screen(self, painter):
        w = self.width()
        h = self.height()

        painter.fillRect(0, 0, w, h, QColor(4, 8, 16, 230))

        # Title
        painter.setFont(QFont("Consolas", 32, QFont.Weight.Bold))
        painter.setPen(QColor(255, 200, 0))
        painter.drawText(0, h // 2 - 150, w, 50, Qt.AlignmentFlag.AlignCenter, "MISSION CONCLUDED")

        # Final Score
        painter.setFont(QFont("Consolas", 24, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(0, h // 2 - 90, w, 40, Qt.AlignmentFlag.AlignCenter, f"FINAL SCORE: {self.score:,}")

        accuracy = int((self.shots_hit / max(1, self.shots_fired)) * 100)
        grade = "S-TIER (AVENGER)" if self.score > 3500 else ("A-TIER (MARKSMAN)" if self.score > 2000 else "B-TIER (RECRUIT)")

        painter.setFont(QFont("Segoe UI", 12))
        painter.setPen(QColor(180, 210, 240))
        stats_text = (
            f"Targets Destroyed: {self.shots_hit}   |   Accuracy: {accuracy}%   |   Stark Rating: {grade}\n"
            f"All-Time High Score: {self.high_score:,}"
        )
        painter.drawText(0, h // 2 - 40, w, 60, Qt.AlignmentFlag.AlignCenter, stats_text)

        # Play Again Button
        btn_w, btn_h = 260, 48
        bx = (w - btn_w) // 2
        by = h // 2 + 50
        painter.setBrush(QColor(0, 255, 140, 45))
        painter.setPen(QPen(QColor(0, 255, 140), 2))
        painter.drawRoundedRect(bx, by, btn_w, btn_h, 10, 10)

        painter.setFont(QFont("Consolas", 13, QFont.Weight.Bold))
        painter.setPen(QColor(0, 255, 140))
        painter.drawText(bx, by + 30, btn_w, 30, Qt.AlignmentFlag.AlignHCenter, "[ PLAY AGAIN ]")

        # Exit hint
        painter.setFont(QFont("Consolas", 10))
        painter.setPen(QColor(140, 160, 180))
        painter.drawText(0, by + 75, w, 20, Qt.AlignmentFlag.AlignCenter, "Press ESC to return to SHRIVA AI Command Core")

    def closeEvent(self, event):
        if self.worker:
            self.worker.stop()
        if self.game_timer:
            self.game_timer.stop()
        if self.spawn_timer:
            self.spawn_timer.stop()
        event.accept()


# =====================================================================
# Global Launcher
# =====================================================================
active_game_dialog = None

def launch_repulsor_game(parent=None):
    global active_game_dialog
    if active_game_dialog:
        active_game_dialog.close()
    active_game_dialog = StarkRepulsorGame(parent=parent)
    active_game_dialog.show()
    active_game_dialog.raise_()
    active_game_dialog.activateWindow()
    return active_game_dialog
