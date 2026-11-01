// JARVISX Mobile App Logic
let ws = null;
let currentTab = 'dashboard';
let isScreenStreaming = false;

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    connectWebSocket();
    setupTrackpad();
    fetchTelemetry();
    setInterval(fetchTelemetry, 3000);
});

function connectWebSocket() {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${location.host}/ws/chat`;
    
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log("[JARVISX REMOTE] Connected to Desktop AI WebSockets Server");
        document.getElementById('conn-status').className = 'badge online';
        document.getElementById('conn-status').innerText = '● Connected';
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.sender && data.message) {
            appendChatMessage(data.sender, data.message);
        }
    };

    ws.onclose = () => {
        document.getElementById('conn-status').className = 'badge offline';
        document.getElementById('conn-status').innerText = '● Disconnected';
        setTimeout(connectWebSocket, 3000); // Auto reconnect
    };
}

function switchNavTab(tabName) {
    currentTab = tabName;
    document.querySelectorAll('.tab-view').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));

    document.getElementById(`view-${tabName}`).classList.add('active');
    
    // Highlight nav item
    const btnIndex = ['dashboard', 'chat', 'remote', 'files', 'settings'].indexOf(tabName);
    if (btnIndex >= 0) {
        document.querySelectorAll('.nav-item')[btnIndex].classList.add('active');
    }
}

function switchRemoteMode(modeName) {
    document.querySelectorAll('.remote-mode-panel').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.sub-tab').forEach(el => el.classList.remove('active'));

    document.getElementById(`mode-${modeName}`).classList.add('active');
    document.getElementById(`tab-${modeName}-btn`).classList.add('active');
}

// ---------------- TELEMETRY ----------------
async function fetchTelemetry() {
    try {
        const res = await fetch('/api/v1/telemetry/status');
        if (res.ok) {
            const data = await res.json();
            document.getElementById('cpu-val').innerText = `${data.cpu}%`;
            document.getElementById('cpu-bar').style.width = `${data.cpu}%`;
            
            document.getElementById('ram-val').innerText = `${data.ram}%`;
            document.getElementById('ram-bar').style.width = `${data.ram}%`;

            document.getElementById('disk-val').innerText = `${data.disk}%`;
            document.getElementById('disk-bar').style.width = `${data.disk}%`;

            document.getElementById('bat-val').innerText = `${data.battery}%`;
            document.getElementById('bat-bar').style.width = `${data.battery}%`;
        }
    } catch (e) {
        console.log("Telemetry update offline:", e);
    }
}

// ---------------- AI CHAT ----------------
document.getElementById('send-chat-btn').addEventListener('click', sendChatMessage);
document.getElementById('chat-input').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendChatMessage();
});

function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const msg = input.value.trim();
    if (!msg) return;

    appendChatMessage("You", msg);
    input.value = "";

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: "command", command: msg }));
    } else {
        fetch('/api/v1/ai/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: msg })
        });
    }
}

function appendChatMessage(sender, text) {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `msg ${sender.toLowerCase() === 'you' ? 'user' : 'jarvis'}`;
    
    div.innerHTML = `
        <span class="sender">${sender} • Just now</span>
        <div class="bubble">${text}</div>
    `;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

// ---------------- QUICK AI MODULE TRIGGERS ----------------
function triggerModule(moduleName) {
    fetch('/api/v1/ai/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: moduleName })
    });
    switchNavTab('chat');
}

// ---------------- TRACKPAD REMOTE MOUSE CONTROL ----------------
let startX = 0, startY = 0;
function setupTrackpad() {
    const surface = document.getElementById('touchpad-surface');
    
    surface.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
    });

    surface.addEventListener('touchmove', (e) => {
        const dx = e.touches[0].clientX - startX;
        const dy = e.touches[0].clientY - startY;
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;

        sendRemoteInput('move', { dx: dx * 2, dy: dy * 2 });
    });

    surface.addEventListener('click', () => {
        sendRemoteInput('left_click');
    });
}

function sendRemoteInput(action, extra = {}) {
    fetch('/api/v1/remote/input', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action, ...extra })
    });
}

function sendRemoteText() {
    const input = document.getElementById('remote-keyboard-input');
    const text = input.value;
    if (!text) return;
    sendRemoteInput('type', { text });
    input.value = "";
}

function sendPowerCommand(action) {
    if (confirm(`Are you sure you want to ${action} your desktop PC?`)) {
        fetch('/api/v1/remote/power', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action })
        });
    }
}

// ---------------- SCREEN MIRROR ----------------
let screenWs = null;
function startScreenMirror() {
    const img = document.getElementById('screen-mirror-img');
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${location.host}/ws/screen`;
    
    screenWs = new WebSocket(wsUrl);
    screenWs.onmessage = (event) => {
        img.src = "data:image/jpeg;base64," + event.data;
    };
}

function stopScreenMirror() {
    if (screenWs) {
        screenWs.close();
        screenWs = None;
    }
}

// ---------------- CONTINUOUS HANDS-FREE VOICE ENGINE ----------------
let mobileRec = null;
let isMobileListening = false;

const voiceBtn = document.getElementById('quick-voice-btn');
if (voiceBtn) {
    voiceBtn.addEventListener('click', () => {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert("Mobile Speech Recognition not supported in this browser. Please use Chrome/Safari or Chat tab!");
            return;
        }

        if (isMobileListening) {
            stopContinuousListening();
        } else {
            startContinuousListening();
        }
    });
}

function startContinuousListening() {
    try {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        mobileRec = new SpeechRecognition();
        mobileRec.lang = 'en-IN';
        mobileRec.continuous = true;
        mobileRec.interimResults = false;

        mobileRec.onstart = () => {
            isMobileListening = true;
            voiceBtn.innerText = "🔴 Continuous Mic ON (Tap to Stop)";
            voiceBtn.style.background = "linear-gradient(135deg, #EF4444, #DC2626)";
            voiceBtn.style.boxShadow = "0 0 20px rgba(239, 68, 68, 0.8)";
            
            const statusEl = document.querySelector('.status-text');
            if (statusEl) statusEl.innerText = "🎙️ Listening continuously... Speak commands anytime!";
        };

        mobileRec.onresult = (e) => {
            for (let i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    const transcript = e.results[i][0].transcript.trim();
                    if (!transcript) continue;
                    
                    console.log("[CONTINUOUS VOICE] Recognized:", transcript);
                    appendChatMessage("You (Voice)", transcript);
                    
                    const statusEl = document.querySelector('.status-text');
                    if (statusEl) statusEl.innerText = `⚡ Executed: "${transcript}"`;
                    
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send(JSON.stringify({ action: "command", command: transcript }));
                    } else {
                        fetch('/api/v1/ai/command', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ command: transcript })
                        });
                    }
                }
            }
        };

        mobileRec.onerror = (err) => {
            console.error("[CONTINUOUS VOICE ERROR]", err);
            if (err.error === 'not-allowed') {
                stopContinuousListening();
                alert("Microphone Access Blocked! Kripya browser settings me Mic allow kijiye!");
            }
        };

        mobileRec.onend = () => {
            if (isMobileListening) {
                try { mobileRec.start(); } catch (e) {}
            }
        };

        mobileRec.start();
    } catch (e) {
        alert("Microphone Error: " + e.message);
    }
}

function stopContinuousListening() {
    isMobileListening = false;
    if (mobileRec) {
        try { mobileRec.stop(); } catch (e) {}
        mobileRec = null;
    }
    voiceBtn.innerText = "🎙️ Speak Command";
    voiceBtn.style.background = "";
    voiceBtn.style.boxShadow = "";
    
    const statusEl = document.querySelector('.status-text');
    if (statusEl) statusEl.innerText = "Desktop AI Online & Ready";
}
