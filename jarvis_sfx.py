import os
import math
import wave
import struct
import threading
import winsound

SFX_DIR = os.path.join(os.path.dirname(__file__), "jarvis_data", "sfx")

def _generate_wav(filepath, duration_sec, freq_func, sample_rate=44100, volume=0.5):
    """Generates a clean 16-bit PCM mono WAV file from a frequency generator function."""
    num_samples = int(duration_sec * sample_rate)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with wave.open(filepath, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        
        phase = 0.0
        data = bytearray()
        for i in range(num_samples):
            t = float(i) / sample_rate
            freq = freq_func(t, duration_sec)
            phase += 2.0 * math.pi * freq / sample_rate
            
            # Apply smooth envelope (attack & decay) to prevent audio clicks
            envelope = 1.0
            attack = 0.03
            decay = 0.08
            if t < attack:
                envelope = t / attack
            elif t > duration_sec - decay:
                envelope = max(0.0, (duration_sec - t) / decay)
                
            sample = volume * envelope * math.sin(phase)
            # Add subtle harmonic for metallic cyber resonance
            sample += 0.25 * volume * envelope * math.sin(phase * 2.0)
            sample = max(-1.0, min(1.0, sample))
            
            int_sample = int(sample * 32767.0)
            data.extend(struct.pack('<h', int_sample))
            
        wav.writeframes(data)


def ensure_sfx_library():
    """Generates all standard Iron Man HUD and JARVIS sound effects if not already present."""
    os.makedirs(SFX_DIR, exist_ok=True)
    
    # 1. Startup Repulsor Sweep (220Hz -> 880Hz upward energy spool)
    boot_path = os.path.join(SFX_DIR, "boot_repulsor.wav")
    if not os.path.exists(boot_path):
        def boot_freq(t, dur):
            progress = (t / dur) ** 1.6
            return 180.0 + progress * 720.0
        _generate_wav(boot_path, 1.2, boot_freq, volume=0.45)
        
    # 2. Command Acknowledge / Wake Chime (980Hz -> 1480Hz quick dual-pulse)
    ack_path = os.path.join(SFX_DIR, "command_ack.wav")
    if not os.path.exists(ack_path):
        def ack_freq(t, dur):
            if t < dur * 0.45:
                return 987.77 # B5
            else:
                return 1318.51 # E6
        _generate_wav(ack_path, 0.22, ack_freq, volume=0.35)

    # 3. Success / Mark VII Sequence Complete (Arpeggio: C5 -> E5 -> G5 -> C6)
    success_path = os.path.join(SFX_DIR, "task_success.wav")
    if not os.path.exists(success_path):
        def success_freq(t, dur):
            step = int((t / dur) * 4)
            notes = [523.25, 659.25, 783.99, 1046.50]
            return notes[min(step, 3)]
        _generate_wav(success_path, 0.38, success_freq, volume=0.35)

    # 4. Tactical Warning / Sentinel Alert (Warble tone)
    alert_path = os.path.join(SFX_DIR, "alert_tactical.wav")
    if not os.path.exists(alert_path):
        def alert_freq(t, dur):
            warble = math.sin(t * 35.0) * 120.0
            return 750.0 + warble
        _generate_wav(alert_path, 0.55, alert_freq, volume=0.4)

    # 5. Voice Listening Pulse
    listen_path = os.path.join(SFX_DIR, "listen_start.wav")
    if not os.path.exists(listen_path):
        def listen_freq(t, dur):
            return 800.0 + (t / dur) * 400.0
    # 6. Repulsor Blast Laser (1200Hz -> 180Hz rapid discharge)
    blast_path = os.path.join(SFX_DIR, "repulsor_blast.wav")
    if not os.path.exists(blast_path):
        def blast_freq(t, dur):
            return 1200.0 * (1.0 - (t / dur) ** 0.5) + 160.0
        _generate_wav(blast_path, 0.28, blast_freq, volume=0.55)

    # 7. Target Explosion / EMP Shatter
    exp_path = os.path.join(SFX_DIR, "target_explosion.wav")
    if not os.path.exists(exp_path):
        def exp_freq(t, dur):
            return 280.0 * (1.0 - t / dur) + 50.0 + (math.sin(t * 80.0) * 35.0)
        _generate_wav(exp_path, 0.35, exp_freq, volume=0.55)

    # 8. Target Lock-On Chirp (A6 -> C7)
    lock_path = os.path.join(SFX_DIR, "target_lock.wav")
    if not os.path.exists(lock_path):
        def lock_freq(t, dur):
            return 1760.0 if t < dur * 0.5 else 2093.0
        _generate_wav(lock_path, 0.14, lock_freq, volume=0.35)


def play_sfx(name):
    """
    Asynchronously plays a futuristic Iron Man sound effect without blocking execution.
    Supported: 'boot', 'ack', 'success', 'alert', 'listen', 'blast', 'explosion', 'lock'
    """
    sound_files = {
        "boot": "boot_repulsor.wav",
        "ack": "command_ack.wav",
        "success": "task_success.wav",
        "alert": "alert_tactical.wav",
        "listen": "listen_start.wav",
        "blast": "repulsor_blast.wav",
        "explosion": "target_explosion.wav",
        "lock": "target_lock.wav"
    }
    filename = sound_files.get(name)
    if not filename:
        return
        
    filepath = os.path.join(SFX_DIR, filename)
    if not os.path.exists(filepath):
        try:
            ensure_sfx_library()
        except Exception:
            return

    def _play():
        try:
            winsound.PlaySound(filepath, winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception:
            pass

    threading.Thread(target=_play, daemon=True).start()

# Initialize sound library on import
try:
    ensure_sfx_library()
except Exception:
    pass
