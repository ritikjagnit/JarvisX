import cv2
import time
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QFrame

import mediapipe as mp
import threading
from voice_engine import speak

class VisionWorker(QThread):
    frame_ready = pyqtSignal(QImage)
    analytics_ready = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = False
        self.camera_index = 0
        
        # Mediapipe setup
        self.mp_face = mp.solutions.face_detection
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        
        self.face_detection = self.mp_face.FaceDetection(min_detection_confidence=0.5)
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        # Deepface setup
        self.deepface_available = False
        try:
            from deepface import DeepFace
            self.DeepFace = DeepFace
            self.deepface_available = True
        except ImportError:
            pass
            
        self.last_emotion_time = 0
        self.current_emotion = "Neutral (0%)"
        self.current_raw_emotion = "Neutral"
        self.last_motion_time = time.time()
        self.last_speech_time = 0
        self.prev_nose_y = None
        self.prev_nose_x = None

    def run(self):
        self.running = True
        cap = cv2.VideoCapture(self.camera_index)
        
        # Reduce resolution for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue
                
            frame = cv2.flip(frame, 1) # Mirror
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 1. Detection variables
            active = False
            gestures = []
            posture = "Unknown"
            motion = "No movement detected"
            
            # 2. Face Detection
            face_results = self.face_detection.process(rgb_frame)
            if face_results.detections:
                active = True
                for detection in face_results.detections:
                    self.mp_drawing.draw_detection(frame, detection)
                    
                # 3. Emotion Detection (Throttled to 1s to save CPU)
                current_time = time.time()
                if self.deepface_available and current_time - self.last_emotion_time > 1.0:
                    try:
                        # Non-blocking emotion detection
                        if not hasattr(self, 'emotion_thread') or not self.emotion_thread.is_alive():
                            def detect_emotion(img):
                                try:
                                    res = self.DeepFace.analyze(img, actions=['emotion'], enforce_detection=False)
                                    if res:
                                        emo = res[0]['dominant_emotion']
                                        conf = res[0]['emotion'][emo]
                                        self.current_raw_emotion = emo.capitalize()
                                        self.current_emotion = f"{emo.capitalize()} ({int(conf)}%)"
                                except Exception:
                                    pass
                            self.emotion_thread = threading.Thread(target=detect_emotion, args=(rgb_frame.copy(),), daemon=True)
                            self.emotion_thread.start()
                    except Exception:
                        pass
                    self.last_emotion_time = current_time
            
            # 4. Gesture / Hands
            hand_results = self.hands.process(rgb_frame)
            if hand_results.multi_hand_landmarks:
                active = True
                for hand_landmarks in hand_results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                    
                    thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
                    index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    middle_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                    
                    if thumb_tip.y < index_tip.y - 0.1:
                        gestures.append("Thumbs up")
                    elif index_tip.y < middle_tip.y - 0.1:
                        if index_tip.y < thumb_tip.y:
                            gestures.append("Pointing")
                        else:
                            gestures.append("Raised hand")
                    elif index_tip.y < thumb_tip.y and middle_tip.y < thumb_tip.y:
                        gestures.append("Victory sign")
                    else:
                        gestures.append("Hand wave")
            
            # 5. Posture & Motion
            pose_results = self.pose.process(rgb_frame)
            if pose_results.pose_landmarks:
                active = True
                landmarks = pose_results.pose_landmarks.landmark
                self.mp_drawing.draw_landmarks(frame, pose_results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
                
                nose = landmarks[self.mp_pose.PoseLandmark.NOSE.value]
                l_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                r_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
                
                # Motion
                if self.prev_nose_x is not None:
                    dx = nose.x - self.prev_nose_x
                    dy = nose.y - self.prev_nose_y
                    if abs(dx) > 0.05:
                        motion = "User moved right" if dx > 0 else "User moved left"
                    elif abs(dy) > 0.05:
                        motion = "User moved down" if dy > 0 else "User moved up"
                    
                self.prev_nose_x = nose.x
                self.prev_nose_y = nose.y
                
                # Posture
                shoulder_y = (l_shoulder.y + r_shoulder.y) / 2
                if shoulder_y > 0.8:
                    posture = "Slouching"
                elif nose.y > shoulder_y + 0.1:
                    posture = "Sleeping"
                elif shoulder_y < 0.5:
                    posture = "Standing"
                else:
                    posture = "Sitting"
            else:
                self.prev_nose_x = None
                self.prev_nose_y = None
                if not active:
                    motion = "User not in frame"

            if active:
                self.last_motion_time = time.time()
                
            inactive_time = time.time() - self.last_motion_time

            gestures = list(set(gestures))
            if not gestures:
                gestures = ["None"]
                
            # Smart AI Response Logic
            if current_time - self.last_speech_time > 60: # Limit speech frequency to 1 min
                speech_text = None
                if inactive_time > 1200: # 20 mins
                    speech_text = "You have been inactive."
                elif self.current_raw_emotion in ["Sad", "Fear", "Angry"]:
                    speech_text = "Sir, you seem stressed today."
                elif self.current_raw_emotion in ["Happy", "Excited"]:
                    speech_text = "You look energetic today."
                    
                if speech_text:
                    threading.Thread(target=speak, args=(speech_text,), daemon=True).start()
                    self.last_speech_time = current_time
                    self.last_motion_time = time.time() # reset to prevent spam
            
            analytics = {
                "emotion_text": self.current_emotion,
                "raw_emotion": self.current_raw_emotion,
                "motion": motion,
                "gestures": gestures,
                "posture": posture,
                "inactive_time": inactive_time
            }
            
            # Convert frame to QImage for PyQt
            rgb_f = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_f.shape
            bytes_per_line = ch * w
            qimg = QImage(rgb_f.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            self.frame_ready.emit(qimg)
            self.analytics_ready.emit(analytics)
            
            time.sleep(1/30) # Maintain ~30 FPS
            
        cap.release()

    def stop(self):
        self.running = False
        self.wait()


class VisionWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: rgba(15, 23, 42, 0.7);
                border: 1.5px solid #00ffff;
                border-radius: 15px;
            }
            QLabel { border: none; }
        """)
        
        layout = QVBoxLayout(self)
        
        # Title & Controls
        header_layout = QHBoxLayout()
        title = QLabel("AI VISION MODULE")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #00ffff;")
        
        self.cam_btn = QPushButton("START CAMERA")
        self.cam_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 255, 255, 0.1);
                color: #00ffff;
                border: 1px solid #00ffff;
                border-radius: 5px;
                padding: 5px;
            }
            QPushButton:hover { background: rgba(0, 255, 255, 0.3); }
        """)
        self.cam_btn.clicked.connect(self.toggle_camera)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.cam_btn)
        
        # Video Feed
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(320, 240)
        self.video_label.setStyleSheet("background: #000; border: 1px solid #0066ff;")
        self.video_label.setText("CAMERA OFFLINE")
        
        # Analytics Display
        self.stats_label = QLabel()
        self.stats_label.setFont(QFont("Consolas", 10))
        self.stats_label.setStyleSheet("color: #00ff88;")
        self.stats_label.setText("Emotion: N/A\nPosture: N/A\nMotion: N/A\nGestures: N/A")
        
        layout.addLayout(header_layout)
        layout.addWidget(self.video_label)
        layout.addWidget(self.stats_label)
        
        self.worker = VisionWorker()
        self.worker.frame_ready.connect(self.update_frame)
        self.worker.analytics_ready.connect(self.update_analytics)
        
        self.is_running = False

    def toggle_camera(self):
        if self.is_running:
            self.worker.stop()
            self.cam_btn.setText("START CAMERA")
            self.video_label.setText("CAMERA OFFLINE")
            self.is_running = False
        else:
            self.worker.start()
            self.cam_btn.setText("STOP CAMERA")
            self.is_running = True

    def update_frame(self, qimg):
        pixmap = QPixmap.fromImage(qimg)
        # scale to fit
        scaled = pixmap.scaled(self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.video_label.setPixmap(scaled)
        
    def update_analytics(self, data):
        text = f"Emotion: {data['emotion_text']}\n"
        text += f"Posture: {data['posture']}\n"
        text += f"Motion: {data['motion']}\n"
        text += f"Gestures: {', '.join(data['gestures'])}"
        self.stats_label.setText(text)
