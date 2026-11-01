import time
import math
import cv2
import numpy as np
import pyautogui
from PyQt6.QtCore import QThread, pyqtSignal
from voice_engine import speak
from jarvis_sfx import play_sfx

# Disable pyautogui failsafe pause for maximum smooth continuous movement
pyautogui.PAUSE = 0.001
pyautogui.FAILSAFE = False

class EyeMouseWorker(QThread):
    """
    Cyber Ocular Eye-Tracking Mouse & Double-Blink Clicker.
    
    Features:
    1. Ocular Gaze Navigation: Uses 68-point facial topology & pupil geometry
       to track eye gaze and head direction, mapping smoothly to screen coordinates.
    2. Double-Blink Click: Natural single blinks are ignored. An intentional
       double-blink (two rapid eyelid taps within 550ms) triggers a left click
       with instant audio chime feedback.
    3. Auto-Calibration: Automatically establishes center baseline during the
       first 15 frames for maximum precision across any seated posture.
    """
    status_updated = pyqtSignal(str)

    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self.running = False

        # Screen resolution
        self.screen_w, self.screen_h = pyautogui.size()

        # Calibration & Baseline Gaze
        self.calibrated = False
        self.calib_samples = []
        self.base_gaze_x = 0.0
        self.base_gaze_y = 0.0

        # Cursor smoothing & sensitivity
        self.prev_x = self.screen_w // 2
        self.prev_y = self.screen_h // 2
        self.smoothing = 0.35
        self.sensitivity_x = 45.0
        self.sensitivity_y = 52.0

        # Double-Blink Detection State
        self.blink_count = 0
        self.first_blink_time = 0.0
        self.eye_was_closed = False
        self.last_click_time = 0.0
        self.click_cooldown = 0.70  # 700ms cooldown between intentional clicks

    def _calc_ear(self, eye_pts):
        """Calculates Eye Aspect Ratio (EAR) for blink detection."""
        p = np.array(eye_pts)
        A = np.linalg.norm(p[1] - p[5])
        B = np.linalg.norm(p[2] - p[4])
        C = np.linalg.norm(p[0] - p[3])
        return (A + B) / (2.0 * C + 1e-5)

    def _calc_pupil_ratio(self, gray_frame, eye_pts):
        """Calculates horizontal and vertical pupil centroid ratio within eye contour."""
        try:
            pts = np.array(eye_pts, dtype=np.int32)
            x, y, w, h = cv2.boundingRect(pts)
            if w < 5 or h < 3:
                return 0.5, 0.5

            eye_roi = gray_frame[y:y+h, x:x+w]
            mask = np.zeros(eye_roi.shape, dtype=np.uint8)
            pts_shifted = pts - [x, y]
            cv2.fillPoly(mask, [pts_shifted], 255)

            masked_pixels = eye_roi[mask == 255]
            if len(masked_pixels) < 10:
                return 0.5, 0.5

            min_val = np.percentile(masked_pixels, 25)
            _, thresh = cv2.threshold(eye_roi, int(min_val), 255, cv2.THRESH_BINARY_INV)
            thresh = cv2.bitwise_and(thresh, thresh, mask=mask)

            M = cv2.moments(thresh)
            if M['m00'] > 0:
                cx = (M['m10'] / M['m00']) / float(w)
                cy = (M['m01'] / M['m00']) / float(h)
                return float(cx), float(cy)
        except Exception:
            pass
        return 0.5, 0.5

    def run(self):
        self.running = True
        import face_recognition

        cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not cap.isOpened():
            cap = cv2.VideoCapture(self.camera_index)

        if not cap.isOpened():
            print("[EYE-MOUSE ERROR] Failed to access camera.")
            self.status_updated.emit("Camera device unavailable.")
            self.running = False
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

        print("[EYE-MOUSE] Cyber Ocular Eye-Tracking Mouse ONLINE.")
        self.status_updated.emit("Calibrating center gaze... Please look straight at the screen.")

        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.015)
                continue

            frame = cv2.flip(frame, 1)  # Mirror frame so looking right moves cursor right
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Downsample to 240x180 for 15-20ms ultra-fast landmark inference
            small_rgb = cv2.resize(rgb, (0, 0), fx=0.5, fy=0.5)
            small_gray = cv2.resize(gray, (0, 0), fx=0.5, fy=0.5)

            try:
                landmarks_list = face_recognition.face_landmarks(small_rgb)
            except Exception:
                landmarks_list = []

            if landmarks_list and len(landmarks_list) > 0:
                lm = landmarks_list[0]
                left_eye = lm.get('left_eye', [])
                right_eye = lm.get('right_eye', [])
                nose_bridge = lm.get('nose_bridge', [])
                nose_tip = lm.get('nose_tip', [])

                if left_eye and right_eye and nose_bridge and nose_tip:
                    # 1. Blink Detection (Eye Aspect Ratio EAR)
                    ear_l = self._calc_ear(left_eye)
                    ear_r = self._calc_ear(right_eye)
                    avg_ear = (ear_l + ear_r) / 2.0

                    now = time.time()
                    eyes_closed = avg_ear < 0.185

                    if eyes_closed and not self.eye_was_closed:
                        # Eyelids just closed
                        self.eye_was_closed = True

                    elif not eyes_closed and self.eye_was_closed:
                        # Eyelids just reopened -> A full blink occurred!
                        self.eye_was_closed = False

                        if self.blink_count == 0:
                            # First blink recorded
                            self.blink_count = 1
                            self.first_blink_time = now
                        elif self.blink_count == 1:
                            # Second blink within 550ms -> DOUBLE BLINK TRIGGER!
                            if (now - self.first_blink_time < 0.55) and (now - self.last_click_time > self.click_cooldown):
                                print(f"[EYE-MOUSE] Double-Blink Click Executed at ({self.prev_x}, {self.prev_y})!")
                                try:
                                    pyautogui.click()
                                    play_sfx("ack")  # Audio confirmation chime
                                except Exception as ex:
                                    print(f"[EYE-MOUSE CLICK ERROR] {ex}")

                                self.last_click_time = now
                                self.blink_count = 0
                            else:
                                # Too late, restart counter with this blink
                                self.blink_count = 1
                                self.first_blink_time = now

                    # Reset single blink if timeout exceeds 550ms (prevents accidental clicks from slow natural blinks)
                    if self.blink_count == 1 and (now - self.first_blink_time > 0.55):
                        self.blink_count = 0

                    # 2. Gaze Vector Calculation
                    l_center = np.mean(left_eye, axis=0)
                    r_center = np.mean(right_eye, axis=0)
                    eyes_mid = (l_center + r_center) / 2.0
                    n_center = np.mean(nose_tip, axis=0)
                    n_top = np.array(nose_bridge[0])

                    # Distance from nose bridge to eyes:
                    # On flipped frame: looking right makes nose closer to left eye landmark (right side of image),
                    # so dist_l decreases and dist_r increases. Thus dist_r - dist_l increases (positive)!
                    dist_l = np.linalg.norm(l_center - n_top)
                    dist_r = np.linalg.norm(r_center - n_top)
                    head_yaw = float(dist_r - dist_l)
                    head_pitch = float(n_center[1] - eyes_mid[1])

                    # Pupil centroids
                    px_l, py_l = self._calc_pupil_ratio(small_gray, left_eye)
                    px_r, py_r = self._calc_pupil_ratio(small_gray, right_eye)
                    pupil_shift_x = ((px_l + px_r) / 2.0 - 0.5) * 20.0
                    pupil_shift_y = ((py_l + py_r) / 2.0 - 0.5) * 15.0

                    raw_gaze_x = head_yaw + pupil_shift_x
                    raw_gaze_y = head_pitch + pupil_shift_y

                    # 3. Auto-Calibration (first 15 frames establish neutral center)
                    if not self.calibrated:
                        self.calib_samples.append((raw_gaze_x, raw_gaze_y))
                        if len(self.calib_samples) >= 15:
                            self.base_gaze_x = float(np.mean([s[0] for s in self.calib_samples]))
                            self.base_gaze_y = float(np.mean([s[1] for s in self.calib_samples]))
                            self.calibrated = True
                            print(f"[EYE-MOUSE] Gaze Center Calibrated: ({self.base_gaze_x:.2f}, {self.base_gaze_y:.2f})")
                            self.status_updated.emit("Eye Mouse Online. Double-blink to click.")
                        continue

                    # 4. Map Gaze Deviations to Screen Resolution
                    delta_x = raw_gaze_x - self.base_gaze_x
                    delta_y = raw_gaze_y - self.base_gaze_y

                    # Non-linear amplifier for effortless screen edge reach
                    amp_x = math.copysign((abs(delta_x) ** 1.15), delta_x)
                    amp_y = math.copysign((abs(delta_y) ** 1.15), delta_y)

                    target_x = int(self.screen_w / 2 + amp_x * self.sensitivity_x)
                    target_y = int(self.screen_h / 2 + amp_y * self.sensitivity_y)

                    target_x = max(0, min(self.screen_w - 1, target_x))
                    target_y = max(0, min(self.screen_h - 1, target_y))

                    # Deadzone for reading / focusing without cursor jitter
                    dist_move = math.hypot(target_x - self.prev_x, target_y - self.prev_y)

                    if dist_move > 7.0:
                        # Dynamic adaptive smoothing: snappy saccades, steady micro-moves
                        alpha = min(0.60, self.smoothing + (dist_move / 600.0) * 0.20)
                        curr_x = int(self.prev_x + alpha * (target_x - self.prev_x))
                        curr_y = int(self.prev_y + alpha * (target_y - self.prev_y))

                        try:
                            pyautogui.moveTo(curr_x, curr_y)
                        except Exception:
                            pass

                        self.prev_x = curr_x
                        self.prev_y = curr_y

            time.sleep(0.015)  # ~45 FPS smooth loop

        if cap and cap.isOpened():
            cap.release()
        print("[EYE-MOUSE] Cyber Ocular Eye-Tracking Mouse OFFLINE.")

    def stop(self):
        self.running = False
        self.wait(1200)


class EyeMouseController:
    """Singleton Manager for Cyber Ocular Eye Mouse."""
    def __init__(self):
        self.worker = None
        self.is_active = False

    def start(self):
        if self.is_active:
            return "Eye-Tracking Mouse is already active. Double-blink to click."

        self.is_active = True
        self.worker = EyeMouseWorker()
        self.worker.start()
        return "Eye-Tracking Mouse ONLINE. Look across the screen to navigate cursor. Blink twice rapidly to click."

    def stop(self):
        if not self.is_active:
            return "Eye-Tracking Mouse is currently inactive."

        self.is_active = False
        if self.worker:
            self.worker.stop()
            self.worker = None
        return "Eye-Tracking Mouse has been disengaged."


eye_mouse_controller = EyeMouseController()
