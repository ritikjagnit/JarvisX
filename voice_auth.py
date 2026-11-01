import os
import json
import time
import math
import numpy as np
from scipy.fftpack import dct
from scipy.signal import get_window
import sounddevice as sd

from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QLinearGradient
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, 
    QFrame, QGraphicsDropShadowEffect, QProgressBar
)
from voice_engine import speak

VOICE_ENCODINGS_FILE = os.path.join("jarvis_data", "voice_auth.json")

# ----------------- MFCC & VOICE FEATURE EXTRACTION -----------------

class VoiceAuthEngine:
    """
    Biometric Voice Feature Extractor and Speaker Verification Engine.
    Uses pure NumPy & SciPy (MFCCs, Spectral Centroid, Energy VAD, Cosine Similarity).
    Operating completely offline without third-party web services.
    """
    def __init__(self, sample_rate=16000, frame_len=0.025, frame_step=0.01, num_mel=26, num_mfcc=13):
        self.sr = sample_rate
        self.frame_len = int(sample_rate * frame_len)
        self.frame_step = int(sample_rate * frame_step)
        self.num_mel = num_mel
        self.num_mfcc = num_mfcc

    def _hz_to_mel(self, hz):
        return 2595.0 * np.log10(1.0 + hz / 700.0)

    def _mel_to_hz(self, mel):
        return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)

    def _get_filterbanks(self):
        low_freq = 0.0
        high_freq = self.sr / 2.0
        low_mel = self._hz_to_mel(low_freq)
        high_mel = self._hz_to_mel(high_freq)
        
        mel_points = np.linspace(low_mel, high_mel, self.num_mel + 2)
        hz_points = self._mel_to_hz(mel_points)
        bin_points = np.floor((self.frame_len + 1) * hz_points / self.sr).astype(int)

        nfft = self.frame_len
        fbank = np.zeros((self.num_mel, int(np.floor(nfft / 2 + 1))))
        
        for m in range(1, self.num_mel + 1):
            f_m_minus = bin_points[m - 1]
            f_m = bin_points[m]
            f_m_plus = bin_points[m + 1]

            for k in range(f_m_minus, f_m):
                if f_m != f_m_minus:
                    fbank[m - 1, k] = (k - bin_points[m - 1]) / (f_m - f_m_minus)
            for k in range(f_m, f_m_plus):
                if f_m_plus != f_m:
                    fbank[m - 1, k] = (bin_points[m + 1] - k) / (f_m_plus - f_m)
                    
        return fbank

    def _compute_deltas(self, feat, N=2):
        if feat is None or len(feat) < 3:
            return np.zeros_like(feat)
        num_frames = feat.shape[0]
        denom = 2 * sum([i**2 for i in range(1, N + 1)])
        delta = np.zeros_like(feat)
        for t in range(num_frames):
            num = np.zeros(feat.shape[1])
            for n in range(1, N + 1):
                t1 = min(t + n, num_frames - 1)
                t2 = max(t - n, 0)
                num += n * (feat[t1] - feat[t2])
            delta[t] = num / denom
        return delta

    def extract_features(self, signal):
        """
        Processes 1D float32 audio signal and extracts normalized 56-dim voice embedding vector.
        """
        if signal is None or len(signal) == 0:
            return None

        # Ensure 1D float32
        signal = np.squeeze(signal).astype(np.float32)
        if signal.ndim > 1:
            signal = signal[:, 0]

        # 1. Pre-emphasis
        pre_emphasis = 0.97
        emphasized = np.append(signal[0], signal[1:] - pre_emphasis * signal[:-1])

        # 2. Framing
        signal_length = len(emphasized)
        if signal_length < self.frame_len:
            return None

        num_frames = int(np.ceil(float(np.abs(signal_length - self.frame_len)) / self.frame_step)) + 1
        pad_signal_length = (num_frames - 1) * self.frame_step + self.frame_len
        pad_signal = np.pad(emphasized, (0, pad_signal_length - signal_length), mode='constant')

        indices = np.tile(np.arange(0, self.frame_len), (num_frames, 1)) + \
                  np.tile(np.arange(0, num_frames * self.frame_step, self.frame_step), (self.frame_len, 1)).T
        frames = pad_signal[indices.astype(np.int32, copy=False)]

        # 3. Windowing & FFT
        window = get_window('hamming', self.frame_len)
        frames *= window

        mag_frames = np.absolute(np.fft.rfft(frames, self.frame_len))
        pow_frames = ((1.0 / self.frame_len) * (mag_frames ** 2))

        # 4. Energy-based Voice Activity Detection (VAD)
        frame_energies = np.sum(pow_frames, axis=1)
        energy_threshold = np.percentile(frame_energies, 30) + 1e-8
        speech_indices = np.where(frame_energies > energy_threshold)[0]
        
        if len(speech_indices) > 0:
            pow_frames = pow_frames[speech_indices]
            mag_frames = mag_frames[speech_indices]

        if pow_frames.shape[0] == 0:
            return None

        # 5. Filterbanks & MFCC
        fbank = self._get_filterbanks()
        filter_banks = np.dot(pow_frames, fbank.T)
        filter_banks = np.where(filter_banks == 0, np.finfo(float).eps, filter_banks)
        filter_banks = 20 * np.log10(filter_banks)

        mfcc = dct(filter_banks, type=2, axis=1, norm='ortho')[:, 1:self.num_mfcc+1]
        
        # Delta MFCCs
        delta_mfcc = self._compute_deltas(mfcc)

        # 6. Spectral Features
        freqs = np.linspace(0, self.sr / 2, mag_frames.shape[1])
        spectral_centroids = np.sum(mag_frames * freqs, axis=1) / (np.sum(mag_frames, axis=1) + 1e-8)
        spectral_centroids = (spectral_centroids / (self.sr / 2)).reshape(-1, 1)

        # Combine Features: MFCC + Delta MFCC + Spectral Centroid
        combined = np.hstack((mfcc, delta_mfcc, spectral_centroids))

        # Aggregate Statistics (Mean & Std Dev across speech frames)
        mean_vec = np.mean(combined, axis=0)
        std_vec = np.std(combined, axis=0)
        embedding = np.concatenate([mean_vec, std_vec])

        # L2 Normalize Embedding Vector
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        embedding = np.nan_to_num(embedding, nan=0.0, posinf=0.0, neginf=0.0)
        return embedding

    @staticmethod
    def cosine_similarity(vec1, vec2):
        if vec1 is None or vec2 is None:
            return 0.0
        v1 = np.asarray(vec1, dtype=np.float32)
        v2 = np.asarray(vec2, dtype=np.float32)
        
        v1_norm = v1 / (np.linalg.norm(v1) + 1e-8)
        v2_norm = v2 / (np.linalg.norm(v2) + 1e-8)

        dist = np.linalg.norm(v1_norm - v2_norm)
        sim = max(0.0, 1.0 - (dist / 1.414))
        return float(sim)


# ----------------- STORAGE & PERSISTENCE -----------------

def save_voice_encoding(name, embedding):
    """Saves multi-sample voice embedding vectors to local JSON file."""
    os.makedirs("jarvis_data", exist_ok=True)
    data = {}
    if os.path.exists(VOICE_ENCODINGS_FILE):
        try:
            with open(VOICE_ENCODINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            pass

    key = name.strip()
    new_emb = embedding.tolist() if isinstance(embedding, np.ndarray) else list(embedding)

    if key in data:
        existing = data[key]
        if isinstance(existing, list) and len(existing) > 0 and isinstance(existing[0], list):
            existing.append(new_emb)
            if len(existing) > 8:
                existing = existing[-8:]
            data[key] = existing
        else:
            data[key] = [existing, new_emb]
    else:
        data[key] = [new_emb]

    with open(VOICE_ENCODINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_voice_encodings():
    """Loads registered voice profiles from local JSON file."""
    if not os.path.exists(VOICE_ENCODINGS_FILE):
        return {}
    try:
        with open(VOICE_ENCODINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        parsed = {}
        for name, enc_data in data.items():
            if isinstance(enc_data, list) and len(enc_data) > 0 and isinstance(enc_data[0], list):
                parsed[name] = [np.array(e, dtype=np.float32) for e in enc_data]
            else:
                parsed[name] = [np.array(enc_data, dtype=np.float32)]
        return parsed
    except Exception:
        return {}

def has_registered_voice_users():
    """Returns True if at least one user has registered voice biometrics."""
    return len(load_voice_encodings()) > 0

def verify_speaker(audio_signal, sample_rate=16000, threshold=0.58):
    """
    Verifies audio signal against all registered multi-sample voice profiles.
    Returns (is_authenticated, matched_name, confidence_percent).
    """
    engine = VoiceAuthEngine(sample_rate=sample_rate)
    input_emb = engine.extract_features(audio_signal)
    if input_emb is None:
        print("[VOICE AUTH LOG] Extraction failed: Audio signal was silent or unclear.")
        return False, None, 0

    profiles = load_voice_encodings()
    if not profiles:
        print("[VOICE AUTH LOG] No registered voice profiles found.")
        return False, None, 0

    best_match_name = None
    max_sim = 0.0

    for name, stored_embs in profiles.items():
        # Compare against all stored samples for this user
        user_sims = [engine.cosine_similarity(input_emb, emb) for emb in stored_embs]
        top_user_sim = max(user_sims) if user_sims else 0.0
        
        print(f"[VOICE AUTH LOG] Comparing input against '{name}' ({len(stored_embs)} samples): Max Similarity = {top_user_sim:.4f} ({int(top_user_sim*100)}%)")
        if top_user_sim > max_sim:
            max_sim = top_user_sim
            best_match_name = name

    confidence = int(max_sim * 100)
    print(f"[VOICE AUTH LOG] Top Candidate: '{best_match_name}' | Similarity: {max_sim:.4f} ({confidence}%) | Required Threshold: {threshold:.2f} ({int(threshold*100)}%)")

    if max_sim >= threshold and best_match_name:
        print(f"[VOICE AUTH LOG] SUCCESS: Verified '{best_match_name}' ({confidence}% >= {int(threshold*100)}%)")
        # Adaptive Learning: Auto-save verified voice sample to adapt to environment/time changes
        try:
            save_voice_encoding(best_match_name, input_emb)
        except Exception:
            pass
        return True, best_match_name, confidence
    else:
        print(f"[VOICE AUTH LOG] REJECTED: Top match '{best_match_name}' ({confidence}%) below required threshold ({int(threshold*100)}%)")
        return False, best_match_name, confidence


# ----------------- RECORDING THREAD -----------------

class VoiceRecordThread(QThread):
    """Thread worker for recording microphone audio without blocking the UI."""
    audio_captured = pyqtSignal(np.ndarray)
    status_updated = pyqtSignal(str, str)
    amplitude_peak = pyqtSignal(float)
    error_occurred = pyqtSignal(str)

    def __init__(self, duration=3.5, sample_rate=16000):
        super().__init__()
        self.duration = duration
        self.sr = sample_rate

    def run(self):
        try:
            self.status_updated.emit("LISTENING TO MICROPHONE - SPEAK NOW...", "#00ffff")
            
            # Record audio synchronously in thread
            audio = sd.rec(
                int(self.duration * self.sr), 
                samplerate=self.sr, 
                channels=1, 
                dtype='float32'
            )
            
            # Monitoring peaks for progress/visualization
            steps = int(self.duration / 0.1)
            for _ in range(steps):
                time.sleep(0.1)
                curr_audio = audio[audio != 0]
                if len(curr_audio) > 0:
                    peak = float(np.max(np.abs(curr_audio[-1600:])))
                    self.amplitude_peak.emit(min(peak * 3.0, 1.0))
                    
            sd.wait() # Ensure recording completes
            
            self.status_updated.emit("PROCESSING BIOMETRIC VOICE PRINT...", "#00ff88")
            self.audio_captured.emit(np.squeeze(audio))
        except Exception as e:
            self.error_occurred.emit(f"Microphone Recording Error: {str(e)}")


# ----------------- AUDIO SPECTRUM VISUALIZER WIDGET -----------------

class AudioSpectrumWidget(QFrame):
    """Futuristic Sci-Fi Audio Waveform Visualizer."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.amplitude = 0.0
        self.phase = 0.0
        self.setMinimumHeight(120)
        self.setStyleSheet("background: #020617; border: 1px solid #0066ff; border-radius: 10px;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(30)

    def set_amplitude(self, amp):
        self.amplitude = max(amp, 0.05)

    def _animate(self):
        self.phase += 0.15
        # Smoothly decay amplitude
        self.amplitude = max(self.amplitude * 0.92, 0.05)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cy = h / 2.0

        # Draw grid lines
        painter.setPen(QPen(QColor(0, 255, 255, 30), 1, Qt.PenStyle.DashLine))
        painter.drawLine(0, int(cy), w, int(cy))

        # Draw futuristic sine waves
        for wave_idx in range(3):
            alpha = 255 - wave_idx * 70
            color = QColor(0, 255, 255, alpha) if wave_idx == 0 else QColor(0, 150, 255, alpha)
            pen = QPen(color, 2 if wave_idx == 0 else 1)
            painter.setPen(pen)

            points = []
            freq = 0.03 + wave_idx * 0.01
            amp = self.amplitude * (h * 0.35) / (wave_idx + 1)

            for x in range(0, w, 4):
                y = cy + math.sin(x * freq + self.phase + wave_idx) * amp * math.sin(x / w * math.pi)
                if math.isnan(y) or math.isinf(y):
                    y = cy
                points.append((x, int(y)))

            for i in range(len(points) - 1):
                painter.drawLine(points[i][0], points[i][1], points[i+1][0], points[i+1][1])


# ----------------- VOICE AUTH DIALOG UI -----------------

class VoiceAuthDialog(QDialog):
    """
    Standalone and Embeddable Holographic Voice Authentication & Registration Dialog.
    """
    def __init__(self, parent=None, mode="auth"):
        super().__init__(parent)
        self.setWindowTitle("SHRIVA AI VOICE BIOMETRICS")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.resize(650, 520)

        self.mode = mode  # "auth" or "register"
        self.authenticated_user = None
        self.is_authenticated = False
        self.engine = VoiceAuthEngine()
        self.record_samples = []
        self.target_samples = 3

        # Modern Glassmorphism Styling
        self.setStyleSheet("""
            QDialog {
                background: #020617;
                border: 2px solid #00ffff;
                border-radius: 20px;
            }
            QLabel {
                color: #ffffff;
                border: none;
            }
            QPushButton {
                background: rgba(0, 255, 255, 0.1);
                color: #00ffff;
                border: 1.5px solid #00ffff;
                border-radius: 8px;
                padding: 10px 18px;
                font-weight: bold;
                font-family: Arial;
                font-size: 13px;
            }
            QPushButton:hover {
                background: rgba(0, 255, 255, 0.3);
                border: 1.5px solid #ffffff;
                color: #ffffff;
            }
            QLineEdit {
                background: rgba(15, 23, 42, 0.8);
                color: #00ffff;
                border: 1px solid #0066ff;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
        """)

        # Drop Shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 255, 255, 160))
        shadow.setOffset(0, 0)
        self.setGraphicsEffect(shadow)

        self._init_ui()

        # Thread instance
        self.record_thread = None

        if self.mode == "auth" and has_registered_voice_users():
            self.show_auth_mode()
        else:
            self.show_register_mode()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        # Header Title Card
        self.header_frame = QFrame()
        self.header_frame.setStyleSheet("background: rgba(15, 23, 42, 0.6); border: 1px solid #0066ff; border-radius: 10px;")
        header_layout = QVBoxLayout(self.header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        self.title_label = QLabel("SYSTEM SECURITY GATE: VOICE BIOMETRICS")
        self.title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: #00ffff; letter-spacing: 1px; border: none;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.title_label)

        self.mode_badge = QLabel("[MODE: AUTHENTICATION]")
        self.mode_badge.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        self.mode_badge.setStyleSheet("color: #00ff88; border: none;")
        self.mode_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.mode_badge)

        layout.addWidget(self.header_frame)

        # Audio Spectrum Visualizer
        self.spectrum_widget = AudioSpectrumWidget()
        layout.addWidget(self.spectrum_widget)

        # Input Field (Aligned inside container)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter Speaker Username (e.g. Shravani)...")
        self.name_input.setFixedHeight(42)
        self.name_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_input.setVisible(False)
        layout.addWidget(self.name_input)

        # Status & Prompt Label
        self.status_label = QLabel("INITIALIZING VOICE BIOMETRICS...")
        self.status_label.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #00ffff;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Progress bar for multi-sample registration
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #0066ff;
                border-radius: 5px;
                text-align: center;
                color: #00ffff;
                background: #090d16;
                font-size: 11px;
            }
            QProgressBar::chunk {
                background: #00ffff;
                border-radius: 4px;
            }
        """)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Action Buttons Layout (Horizontal evenly stretched row)
        self.controls_layout = QHBoxLayout()
        self.controls_layout.setSpacing(10)

        self.record_btn = QPushButton("🎤 VERIFY VOICE")
        self.record_btn.setFixedHeight(42)
        self.record_btn.clicked.connect(self.handle_record_click)
        self.controls_layout.addWidget(self.record_btn, 2)

        self.mode_switch_btn = QPushButton("📝 REGISTER PROFILE")
        self.mode_switch_btn.setFixedHeight(42)
        self.mode_switch_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 102, 255, 0.15);
                color: #0088ff;
                border: 1.5px solid #0066ff;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(0, 102, 255, 0.35);
                color: #ffffff;
                border: 1.5px solid #00ffff;
            }
        """)
        self.mode_switch_btn.clicked.connect(self.toggle_mode)
        self.controls_layout.addWidget(self.mode_switch_btn, 2)

        self.exit_btn = QPushButton("✕ CANCEL")
        self.exit_btn.setFixedHeight(42)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 0, 102, 0.1);
                color: #ff0066;
                border: 1.5px solid #ff0066;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(255, 0, 102, 0.3);
                border: 1.5px solid #ffffff;
                color: #ffffff;
            }
        """)
        self.exit_btn.clicked.connect(self.reject)
        self.controls_layout.addWidget(self.exit_btn, 1)

        layout.addLayout(self.controls_layout)

    def toggle_mode(self):
        """Toggles between Verification mode and Registration mode."""
        if self.mode == "auth":
            self.show_register_mode()
        else:
            self.show_auth_mode()

    def show_auth_mode(self):
        self.mode = "auth"
        self.name_input.setVisible(False)
        self.progress_bar.setVisible(False)
        self.mode_badge.setText("[MODE: SPEAKER VERIFICATION]")
        self.mode_badge.setStyleSheet("color: #00ff88; border: none;")
        self.record_btn.setText("🎤 VERIFY VOICE")
        self.mode_switch_btn.setText("📝 NEW REGISTRATION")
        self.title_label.setText("BIOMETRIC ACCESS: VOICE VERIFICATION")
        self.status_label.setText("PRESS 'VERIFY VOICE' AND SPEAK CLEARLY")
        self.status_label.setStyleSheet("color: #00ffff;")

    def show_register_mode(self):
        self.mode = "register"
        self.record_samples.clear()
        self.name_input.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.mode_badge.setText("[MODE: ENROLLMENT PROFILE]")
        self.mode_badge.setStyleSheet("color: #ffaa00; border: none;")
        self.record_btn.setText("🔴 RECORD SAMPLE")
        self.mode_switch_btn.setText("🔒 VERIFY VOICE")
        self.title_label.setText("NEW USER ENROLLMENT: VOICE PRINT")
        self.status_label.setText("ENTER USERNAME & RECORD 3 VOICE SAMPLES")
        self.status_label.setStyleSheet("color: #ffaa00;")

    def handle_record_click(self):
        if self.mode == "register":
            name = self.name_input.text().strip()
            if not name:
                self.update_status("ERROR: ENTER VALID USERNAME FIRST!", "#ff0066")
                return

        self.record_btn.setEnabled(False)
        self.record_thread = VoiceRecordThread(duration=3.5)
        self.record_thread.status_updated.connect(self.update_status)
        self.record_thread.amplitude_peak.connect(self.spectrum_widget.set_amplitude)
        self.record_thread.audio_captured.connect(self.on_audio_captured)
        self.record_thread.error_occurred.connect(self.on_error)
        self.record_thread.start()

    def update_status(self, message, hex_color="#00ffff"):
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {hex_color}; font-weight: bold;")

    def on_audio_captured(self, audio):
        self.record_btn.setEnabled(True)

        if self.mode == "auth":
            is_auth, name, conf = verify_speaker(audio)
            if is_auth:
                self.authenticated_user = name
                self.is_authenticated = True
                self.update_status(f"VOICE VERIFIED: {name.upper()} ({conf}% MATCH)", "#00ff88")
                speak(f"Voice identity confirmed. Access granted, {name}.")
                QTimer.singleShot(1500, self.accept)
            else:
                candidate = f" [{name.upper()}]" if name else ""
                self.update_status(f"SECURITY ALERT: UNVERIFIED VOICE{candidate} ({conf}% MATCH - NEED 68%)", "#ff0066")
                speak("Voice authentication failed. Speaker identity unverified.")

        elif self.mode == "register":
            name = self.name_input.text().strip()
            emb = self.engine.extract_features(audio)
            if emb is not None:
                self.record_samples.append(emb)
                progress = int((len(self.record_samples) / self.target_samples) * 100)
                self.progress_bar.setValue(progress)

                if len(self.record_samples) < self.target_samples:
                    rem = self.target_samples - len(self.record_samples)
                    self.update_status(f"SAMPLE {len(self.record_samples)} STORED! RECORD {rem} MORE.", "#00ff88")
                    speak(f"Sample recorded. Please record {rem} more.")
                else:
                    # Average stored embeddings
                    final_emb = np.mean(self.record_samples, axis=0)
                    norm = np.linalg.norm(final_emb)
                    if norm > 0:
                        final_emb = final_emb / norm

                    save_voice_encoding(name, final_emb)
                    self.update_status(f"VOICE BIOMETRICS REGISTERED FOR {name.upper()}!", "#00ff88")
                    speak(f"Voice profile created successfully for {name}.")
                    QTimer.singleShot(2000, self.show_auth_mode)
            else:
                self.update_status("RECORDING SILENT OR UNCLEAR. PLEASE RETRY.", "#ff0066")

    def on_error(self, err_msg):
        self.record_btn.setEnabled(True)
        self.update_status(f"ERROR: {err_msg.upper()}", "#ff0066")
