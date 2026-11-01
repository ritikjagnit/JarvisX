import os
import time
import cv2
import numpy as np
import pyautogui
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from voice_engine import speak

class AirGestureWorker(QThread):
    """
    Real-time Touchless Air-Gesture Controller.
    Uses computer vision contour & optical centroid motion tracking
    to translate physical hand movements into OS keystrokes (slides, media, desktop).
    """
    gesture_detected = pyqtSignal(str, str)

    def __init__(self, camera_index=0, parent=None):
        super().__init__(parent)
        self.camera_index = camera_index
        self.running = False
        self.last_action_time = 0
        self.cooldown = 1.2  # 1.2s cooldown between actions

    def run(self):
        self.running = True
        cap = cv2.VideoCapture(self.camera_index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

        prev_cx = None
        prev_time = time.time()
        print("[AIR-GESTURE] Optical Hand Gesture Controller ONLINE.")

        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.05)
                continue

            frame = cv2.flip(frame, 1)  # Mirror frame
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Skin tone color thresholding
            lower_skin = np.array([0, 28, 70], dtype=np.uint8)
            upper_skin = np.array([25, 255, 255], dtype=np.uint8)
            mask = cv2.inRange(hsv, lower_skin, upper_skin)
            mask = cv2.GaussianBlur(mask, (5, 5), 0)

            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            current_time = time.time()

            if contours and len(contours) > 0:
                # Find largest contour (assumed to be the hand)
                max_cnt = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(max_cnt)

                if area > 4500:  # Minimum hand size in frame
                    M = cv2.moments(max_cnt)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])

                        # 1. Swipe Motion Detection (Velocity / Delta X)
                        if prev_cx is not None:
                            dx = cx - prev_cx
                            dt = current_time - prev_time

                            if dt < 0.4 and current_time - self.last_action_time > self.cooldown:
                                if dx > 75:
                                    print(f"[GESTURE] Swift Swipe RIGHT detected (dx={dx}) -> Next Slide")
                                    self.last_action_time = current_time
                                    self._trigger_action("SWIPE_RIGHT")
                                elif dx < -75:
                                    print(f"[GESTURE] Swift Swipe LEFT detected (dx={dx}) -> Previous Slide")
                                    self.last_action_time = current_time
                                    self._trigger_action("SWIPE_LEFT")

                        prev_cx = cx
                        prev_time = current_time

                        # 2. Static Finger Pose Detection (Convexity Defects)
                        if current_time - self.last_action_time > self.cooldown:
                            hull = cv2.convexHull(max_cnt, returnPoints=False)
                            if hull is not None and len(hull) > 3:
                                try:
                                    defects = cv2.convexityDefects(max_cnt, hull)
                                    if defects is not None:
                                        finger_count = 0
                                        for i in range(defects.shape[0]):
                                            s, e, f, d = defects[i, 0]
                                            start = tuple(max_cnt[s][0])
                                            end = tuple(max_cnt[e][0])
                                            far = tuple(max_cnt[f][0])

                                            a = np.linalg.norm(np.array(end) - np.array(start))
                                            b = np.linalg.norm(np.array(far) - np.array(start))
                                            c = np.linalg.norm(np.array(end) - np.array(far))

                                            # Cosine theorem for angle
                                            angle = np.arccos(max(-1.0, min(1.0, (b**2 + c**2 - a**2) / (2 * b * c + 1e-5))))
                                            if angle <= np.pi / 2 and d > 20 * 256:
                                                finger_count += 1

                                        # Open Palm (4-5 valleys = 5 fingers)
                                        if finger_count >= 4:
                                            print("[GESTURE] Open Palm Detected -> Play / Pause")
                                            self.last_action_time = current_time
                                            self._trigger_action("OPEN_PALM")
                                        # Peace Sign (1-2 valleys with upright hand)
                                        elif finger_count == 2:
                                            print("[GESTURE] Peace / Victory Sign Detected -> Toggle Desktop")
                                            self.last_action_time = current_time
                                            self._trigger_action("PEACE_SIGN")
                                except Exception:
                                    pass

            time.sleep(0.04)  # ~25 FPS

        cap.release()
        print("[AIR-GESTURE] Optical Hand Gesture Controller OFFLINE.")

    def _trigger_action(self, action_name):
        try:
            if action_name == "SWIPE_RIGHT":
                pyautogui.press("right")
                self.gesture_detected.emit("Swipe Right", "Next slide / track navigated.")
            elif action_name == "SWIPE_LEFT":
                pyautogui.press("left")
                self.gesture_detected.emit("Swipe Left", "Previous slide / track navigated.")
            elif action_name == "OPEN_PALM":
                pyautogui.press("space")
                self.gesture_detected.emit("Open Palm", "Media / Presentation Play/Pause toggled.")
            elif action_name == "PEACE_SIGN":
                pyautogui.hotkey("win", "d")
                self.gesture_detected.emit("Victory Sign", "Desktop view toggled.")
        except Exception as e:
            print(f"[GESTURE ACTION ERROR] {e}")

    def stop(self):
        self.running = False
        self.wait(1200)


class AirGestureController:
    """Singleton Manager for Touchless Air-Gesture Control."""
    def __init__(self):
        self.worker = None
        self.is_active = False

    def start(self):
        if self.is_active:
            return "Touchless Air-Gesture Controller is already active."

        self.is_active = True
        self.worker = AirGestureWorker()
        self.worker.start()
        return "Touchless Air-Gesture Controller ONLINE. Wave your hand right or left to navigate slides, or show an open palm to play and pause."

    def stop(self):
        if not self.is_active:
            return "Touchless Air-Gesture Controller is currently inactive."

        self.is_active = False
        if self.worker:
            self.worker.stop()
            self.worker = None
        return "Touchless Air-Gesture Controller has been disabled."


air_gesture_controller = AirGestureController()
