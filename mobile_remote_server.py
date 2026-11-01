import http.server
import socketserver
import json
import socket
import urllib.parse
import os
import threading
from command_router import CommandRouter

PORT = 8000
router = CommandRouter()

# Pending PC-to-Mobile Action Queue
pending_mobile_actions = []
actions_lock = threading.Lock()

def push_mobile_action(action_type, payload=""):
    with actions_lock:
        pending_mobile_actions.append({"action": action_type, "payload": payload})
    print(f"[PC-TO-MOBILE PUSH] Action queued for Mobile Phone: '{action_type}' ({payload})")

def pop_mobile_actions():
    with actions_lock:
        actions = list(pending_mobile_actions)
        pending_mobile_actions.clear()
        return actions

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>JARVIS Mobile Link</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, sans-serif; }
        body { background: #0f0312; color: #ffccf2; min-height: 100vh; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .header { text-align: center; margin-bottom: 20px; }
        .header h1 { font-size: 26px; color: #ff007f; text-shadow: 0 0 10px #ff00a2; }
        .header p { font-size: 13px; color: #ff99dd; margin-top: 5px; }
        
        .mic-container { margin: 25px 0; text-align: center; }
        .mic-btn {
            width: 110px; height: 110px; border-radius: 50%;
            background: linear-gradient(135deg, #ff007f, #ff0055);
            border: 4px solid #ff66cc; color: white; font-size: 40px;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto; box-shadow: 0 0 25px rgba(255, 0, 127, 0.6);
            cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;
            outline: none; -webkit-tap-highlight-color: transparent;
        }
        .mic-btn:active, .mic-btn.listening {
            transform: scale(1.1); box-shadow: 0 0 40px rgba(255, 0, 162, 0.9);
            background: linear-gradient(135deg, #ff00a2, #ff007f);
        }
        .mic-status { margin-top: 12px; font-size: 14px; font-weight: bold; color: #ff66cc; }

        .input-group { width: 100%; max-width: 400px; display: flex; gap: 10px; margin-bottom: 20px; }
        input[type="text"] {
            flex: 1; padding: 14px; border-radius: 12px; border: 2px solid #ff007f;
            background: rgba(25, 4, 25, 0.85); color: #ffccf2; font-size: 15px; outline: none;
        }
        button.send-btn {
            padding: 0 20px; border-radius: 12px; border: none;
            background: #ff007f; color: white; font-weight: bold; font-size: 15px;
            cursor: pointer;
        }

        .grid-container { width: 100%; max-width: 400px; display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 20px; }
        .action-card {
            background: rgba(45, 8, 40, 0.7); border: 1.5px solid #ff007f; border-radius: 12px;
            padding: 15px; text-align: center; font-size: 13px; font-weight: bold; color: #ffccf2;
            cursor: pointer; transition: background 0.2s; -webkit-tap-highlight-color: transparent;
        }
        .action-card:active { background: rgba(255, 0, 127, 0.4); }

        .terminal {
            width: 100%; max-width: 400px; flex: 1; min-height: 180px;
            background: rgba(20, 4, 20, 0.9); border: 2px solid #ff007f; border-radius: 14px;
            padding: 15px; font-family: monospace; font-size: 13px; overflow-y: auto;
            box-shadow: inset 0 0 15px rgba(255, 0, 127, 0.2);
        }
        .log-entry { margin-bottom: 8px; line-height: 1.4; }
        .log-user { color: #ff99dd; }
        .log-jarvis { color: #ff00a2; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Intelligent AI Mobile Link</h1>
        <p>● Connected to PC (Bidirectional Control Active)</p>
    </div>

    <div class="mic-container">
        <button class="mic-btn" id="micBtn">🎤</button>
        <div class="mic-status" id="micStatus">Tap to Speak</div>
    </div>

    <div class="input-group">
        <input type="text" id="cmdInput" placeholder="Type command for PC or Phone...">
        <button class="send-btn" onclick="sendCommand()">SEND</button>
    </div>

    <div class="grid-container">
        <div class="action-card" onclick="sendQuick('open browser')">🌐 Open Browser</div>
        <div class="action-card" onclick="sendQuick('defence on')">🛡️ Defense Core</div>
        <div class="action-card" onclick="sendQuick('vault kholo')">🔐 Cyber Vault</div>
        <div class="action-card" onclick="sendQuick('system metrics')">📊 System Audit</div>
    </div>

    <div class="terminal" id="terminal">
        <div class="log-entry log-jarvis">[JARVIS]: Bidirectional PC-Mobile link active. Voice & PC Remote Receiver online!</div>
    </div>

    <script>
        const terminal = document.getElementById('terminal');
        const micBtn = document.getElementById('micBtn');
        const micStatus = document.getElementById('micStatus');
        const cmdInput = document.getElementById('cmdInput');

        cmdInput.addEventListener("keypress", function(e) {
            if (e.key === "Enter") sendCommand();
        });

        function appendLog(sender, text) {
            const div = document.createElement('div');
            div.className = 'log-entry ' + (sender === 'You' ? 'log-user' : 'log-jarvis');
            div.innerText = '[' + sender + ']: ' + text;
            terminal.appendChild(div);
            terminal.scrollTop = terminal.scrollHeight;
        }

        function sendQuick(cmd) {
            cmdInput.value = cmd;
            sendCommand();
        }

        function sendCommand() {
            const cmd = cmdInput.value.trim();
            if (!cmd) return;
            appendLog('You', cmd);
            cmdInput.value = '';

            fetch('/api/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'command=' + encodeURIComponent(cmd)
            })
            .then(res => res.json())
            .then(data => {
                appendLog('JARVIS', data.response || 'Action executed!');
            })
            .catch(err => {
                appendLog('JARVIS', 'Execution error: ' + err);
            });
        }

        // Web Audio Siren Generator for Ringing Phone
        function playSirenSound() {
            try {
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const osc = ctx.createOscillator();
                const gain = ctx.createGain();
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(800, ctx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(1400, ctx.currentTime + 0.5);
                gain.gain.setValueAtTime(0.3, ctx.currentTime);
                osc.connect(gain);
                gain.connect(ctx.destination);
                osc.start();
                osc.stop(ctx.currentTime + 3.0);
            } catch(e) { console.log(e); }
        }

        // Poll PC for PC-to-Mobile Executions (PC commands executed on Phone)
        function pollPcActions() {
            fetch('/api/poll_actions')
            .then(res => res.json())
            .then(actions => {
                if (actions && actions.length > 0) {
                    actions.forEach(act => {
                        appendLog('PC COMMAND', 'Executing on Phone: ' + act.action);
                        if (act.action === 'vibrate') {
                            if (navigator.vibrate) navigator.vibrate([400, 200, 400, 200, 600]);
                        } else if (act.action === 'ring_alarm') {
                            playSirenSound();
                            if (navigator.vibrate) navigator.vibrate([500, 200, 500, 200, 1000]);
                        } else if (act.action === 'open_url') {
                            window.open(act.payload, '_blank');
                        } else if (act.action === 'speak') {
                            if ('speechSynthesis' in window) {
                                const msg = new SpeechSynthesisUtterance(act.payload);
                                window.speechSynthesis.speak(msg);
                            }
                        }
                    });
                }
            })
            .catch(err => {})
            .finally(() => {
                setTimeout(pollPcActions, 1200);
            });
        }
        pollPcActions();

        // Web Speech Recognition + MediaRecorder Fallback for Mobile Mic
        let mediaRecorder = null;
        let audioChunks = [];
        let isRecording = false;

        async function initMobileMic() {
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                const recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;
                recognition.lang = 'en-US';

                micBtn.addEventListener('click', () => {
                    try {
                        recognition.start();
                        micBtn.classList.add('listening');
                        micStatus.innerText = 'Listening... (Speak)';
                    } catch(e) {
                        toggleMediaRecorder();
                    }
                });

                recognition.onresult = (event) => {
                    const text = event.results[0][0].transcript;
                    cmdInput.value = text;
                    micBtn.classList.remove('listening');
                    micStatus.innerText = 'Tap to Speak';
                    sendCommand();
                };

                recognition.onerror = (err) => {
                    console.log('WebSpeech error, falling back to AudioRecorder: ', err);
                    toggleMediaRecorder();
                };

                recognition.onend = () => {
                    micBtn.classList.remove('listening');
                    micStatus.innerText = 'Tap to Speak';
                };
            } else {
                micBtn.addEventListener('click', toggleMediaRecorder);
            }
        }

        async function toggleMediaRecorder() {
            if (!isRecording) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream);
                    audioChunks = [];
                    mediaRecorder.ondataavailable = event => audioChunks.push(event.data);
                    mediaRecorder.onstop = uploadAudioBlob;
                    mediaRecorder.start();
                    isRecording = true;
                    micBtn.classList.add('listening');
                    micStatus.innerText = 'Recording... (Tap to stop)';
                } catch(e) {
                    micStatus.innerText = 'Mic blocked! See Chrome settings below';
                    appendLog('JARVIS', 'Microphone blocked by HTTP security! Open chrome://flags/#unsafely-treat-insecure-origin-as-secure and add http://' + window.location.host);
                }
            } else {
                if (mediaRecorder) mediaRecorder.stop();
                isRecording = false;
                micBtn.classList.remove('listening');
                micStatus.innerText = 'Processing audio...';
            }
        }

        function uploadAudioBlob() {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const formData = new FormData();
            formData.append('audio', audioBlob);

            fetch('/api/voice_upload', {
                method: 'POST',
                body: audioBlob
            })
            .then(res => res.json())
            .then(data => {
                if (data.transcript) {
                    cmdInput.value = data.transcript;
                    appendLog('You (Voice)', data.transcript);
                    appendLog('JARVIS', data.response || 'Executed!');
                } else {
                    micStatus.innerText = 'Tap to Speak';
                }
            })
            .catch(err => {
                micStatus.innerText = 'Audio upload error';
            });
        }

        initMobileMic();
    </script>
</body>
</html>
"""

class MobileRemoteHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args): return # Suppress standard log noise

    def do_GET(self):
        if self.path == '/api/poll_actions':
            actions = pop_mobile_actions()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(actions).encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))

    def do_POST(self):
        if self.path == '/api/command':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            parsed = urllib.parse.parse_qs(body)
            command = parsed.get('command', [''])[0]
            
            print(f"\n[MOBILE REMOTE] Received command from Mobile App: '{command}'")
            response_text = router.route(command)
            if not response_text:
                response_text = f"Executed '{command}' on PC."

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            resp_json = json.dumps({"status": "ok", "response": str(response_text)})
            self.wfile.write(resp_json.encode('utf-8'))
        elif self.path == '/api/voice_upload':
            length = int(self.headers.get('Content-Length', 0))
            audio_bytes = self.rfile.read(length)
            
            # Process uploaded audio on PC
            temp_path = os.path.join(os.path.dirname(__file__), "mobile_temp_mic.wav")
            with open(temp_path, "wb") as f:
                f.write(audio_bytes)

            transcript = ""
            try:
                import speech_recognition as sr
                r = sr.Recognizer()
                with sr.AudioFile(temp_path) as source:
                    audio_data = r.record(source)
                    transcript = r.recognize_google(audio_data)
            except Exception as e:
                print(f"[MOBILE AUDIO STT ERROR] {e}")

            response_text = ""
            if transcript:
                print(f"[MOBILE VOICE UPLOAD] Transcribed: '{transcript}'")
                response_text = router.route(transcript)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            resp_json = json.dumps({"status": "ok", "transcript": transcript, "response": str(response_text)})
            self.wfile.write(resp_json.encode('utf-8'))

def start_mobile_remote_server():
    import ssl
    ip = get_local_ip()
    http_url = f"http://{ip}:{PORT}"
    https_port = 8443
    https_url = f"https://{ip}:{https_port}"
    
    print(f"\n=======================================================")
    print(f"📱 JARVIS MOBILE SECURE LINK (HTTPS MIC UNLOCKED) ONLINE!")
    print(f"👉 OPEN THIS LINK ON PHONE FOR UNBLOCKED MICROPHONE:")
    print(f"   🔒 HTTPS URL (FOR MIC WORK): {https_url}")
    print(f"   🌐 HTTP URL:                  {http_url}")
    print(f"=======================================================\n")
    
    cert_path = os.path.join(os.path.dirname(__file__), "cert.pem")
    key_path = os.path.join(os.path.dirname(__file__), "key.pem")

    # Start HTTP on 8000
    def _run_http():
        try:
            http_server = socketserver.TCPServer(("0.0.0.0", PORT), MobileRemoteHandler)
            http_server.serve_forever()
        except Exception: pass
    
    t_http = threading.Thread(target=_run_http, daemon=True)
    t_http.start()

    # Start HTTPS on 8443 (Unlocks Microphone on Android & iOS!)
    try:
        https_server = socketserver.TCPServer(("0.0.0.0", https_port), MobileRemoteHandler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=cert_path, keyfile=key_path)
        https_server.socket = context.wrap_socket(https_server.socket, server_side=True)
        https_server.serve_forever()
    except Exception as e:
        print(f"[HTTPS SERVER NOTICE] {e}")

if __name__ == "__main__":
    start_mobile_remote_server()
