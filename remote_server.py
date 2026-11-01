import os
import sys
import time
import json
import psutil
import base64
import io
import threading
import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends, Header, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel
from PyQt6.QtCore import QThread, pyqtSignal

import remote_db
import remote_security

try:
    import pyautogui
    pyautogui.FAILSAFE = False
except ImportError:
    pyautogui = None

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

# Global reference to main.py worker queue callback
COMMAND_WORKER_CALLBACK = None
WEBSOCKET_CLIENTS = set()

app = FastAPI(
    title="JarvisX Remote AI OS API",
    description="Production-grade REST & WebSocket API for Cross-Platform Remote AI Control",
    version="2.0.0"
)

# Enable CORS for Mobile Apps & Web Browsers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve Web Mobile App static files
web_dir = os.path.join(os.path.dirname(__file__), "web_remote")
if os.path.exists(web_dir):
    app.mount("/mobile", StaticFiles(directory=web_dir, html=True), name="web_remote")

@app.get("/")
def root():
    return {
        "app": "JarvisX Remote AI OS",
        "status": "ONLINE",
        "mobile_app_url": "/mobile",
        "docs_url": "/docs"
    }

# ---------------- PENDING COMMAND & MODELS ----------------
class CommandRequest(BaseModel):
    command: str

class InputRequest(BaseModel):
    action: str
    dx: float = 0
    dy: float = 0
    text: str = ""

class PowerRequest(BaseModel):
    action: str

class PairCodeRequest(BaseModel):
    otp: str
    device_name: str
    device_type: str = "Mobile"

# ---------------- AUTHENTICATION & PAIRING ENDPOINTS ----------------
@app.post("/api/v1/auth/pair-code")
def pair_device_with_code(req: PairCodeRequest):
    if remote_security.verify_otp_code(req.otp):
        device_id = f"dev_{int(time.time())}"
        token = remote_security.generate_jwt_token(device_id, req.device_name)
        remote_db.register_device(device_id, req.device_name, req.device_type)
        remote_db.log_audit_event("DEVICE_PAIRED", "SUCCESS", device_id, details=req.device_name)
        return {"status": "SUCCESS", "token": token, "device_id": device_id}
    else:
        remote_db.log_audit_event("PAIRING_FAILED", "UNAUTHORIZED", details="Invalid 6-digit OTP")
        raise HTTPException(status_code=401, detail="Invalid or expired pairing code")

@app.get("/api/v1/auth/paired-devices")
def get_paired_devices():
    return remote_db.get_paired_devices()

@app.post("/api/v1/auth/revoke/{device_id}")
def revoke_paired_device(device_id: str):
    success = remote_db.revoke_device(device_id)
    return {"status": "SUCCESS" if success else "NOT_FOUND"}

# ---------------- TELEMETRY ENDPOINT ----------------
@app.get("/api/v1/telemetry/status")
def get_telemetry_status():
    battery = psutil.sensors_battery()
    bat_percent = int(battery.percent) if battery else 100
    
    return {
        "cpu": int(psutil.cpu_percent(interval=None)),
        "ram": int(psutil.virtual_memory().percent),
        "disk": int(psutil.disk_usage('C:\\').percent),
        "battery": bat_percent,
        "active_processes": len(psutil.pids()),
        "status": "OPTIMAL"
    }

# ---------------- AI COMMAND ENDPOINT ----------------
@app.post("/api/v1/ai/command")
def send_ai_command(req: CommandRequest):
    global COMMAND_WORKER_CALLBACK
    if not req.command:
        raise HTTPException(status_code=400, detail="Empty command")
        
    remote_db.save_chat_history("You", req.command, "REMOTE")
    
    if COMMAND_WORKER_CALLBACK:
        COMMAND_WORKER_CALLBACK(req.command, source="mobile", priority=1)
        return {"status": "ENQUEUED", "command": req.command}
    else:
        return {"status": "ERROR", "detail": "Command Queue Worker not connected"}

@app.get("/api/v1/ai/history")
def get_history():
    return remote_db.get_chat_history(limit=50)

# ---------------- REMOTE CONTROL INPUT ENDPOINTS ----------------
@app.post("/api/v1/remote/input")
def handle_remote_input(req: InputRequest):
    if not pyautogui:
        return {"status": "ERROR", "detail": "PyAutoGUI missing"}
        
    try:
        if req.action == "move":
            pyautogui.moveRel(req.dx, req.dy)
        elif req.action == "left_click":
            pyautogui.click()
        elif req.action == "right_click":
            pyautogui.rightClick()
        elif req.action == "type":
            pyautogui.write(req.text)
        return {"status": "EXECUTED"}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}

@app.post("/api/v1/remote/power")
def handle_remote_power(req: PowerRequest):
    action = req.action.lower()
    if action == "shutdown":
        os.system("shutdown /s /t 10")
        return {"status": "SHUTDOWN_INITIATED"}
    elif action == "restart":
        os.system("shutdown /r /t 10")
        return {"status": "RESTART_INITIATED"}
    elif action == "lock":
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return {"status": "LOCKED"}
    return {"status": "UNKNOWN_ACTION"}

# ---------------- FILE MANAGER ENDPOINTS ----------------
@app.get("/api/v1/files/list")
def list_files(path: str = "C:\\Users\\MBiG\\Documents"):
    if not os.path.exists(path):
        path = "C:\\"
    items = []
    try:
        for name in os.listdir(path):
            full = os.path.join(path, name)
            is_dir = os.path.isdir(full)
            items.append({
                "name": name,
                "is_dir": is_dir,
                "size": os.path.getsize(full) if not is_dir else 0,
                "path": full
            })
    except Exception as e:
        pass
    return {"current_path": path, "items": items}

# ---------------- WEBSOCKETS STREAMS ----------------
@app.websocket("/ws/chat")
async def websocket_chat_endpoint(websocket: WebSocket):
    await websocket.accept()
    WEBSOCKET_CLIENTS.add(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            cmd = data.get("command")
            if cmd and COMMAND_WORKER_CALLBACK:
                remote_db.save_chat_history("You", cmd, "WEBSOCKET")
                COMMAND_WORKER_CALLBACK(cmd, source="mobile", priority=1)
    except WebSocketDisconnect:
        WEBSOCKET_CLIENTS.remove(websocket)

@app.websocket("/ws/screen")
async def websocket_screen_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if ImageGrab:
                img = ImageGrab.grab()
                img.thumbnail((800, 450))
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG", quality=40)
                base64_str = base64.b64encode(buffered.getvalue()).decode()
                await websocket.send_text(base64_str)
            await asyncio.sleep(0.15) # ~7 FPS low latency screen stream
    except WebSocketDisconnect:
        pass

ASYNC_LOOP = None

@app.on_event("startup")
async def on_startup():
    global ASYNC_LOOP
    ASYNC_LOOP = asyncio.get_running_loop()

def broadcast_chat_response(sender: str, message: str):
    remote_db.save_chat_history(sender, message, "DESKTOP")
    payload = json.dumps({"sender": sender, "message": message})
    
    async def _send_to_all():
        for ws in list(WEBSOCKET_CLIENTS):
            try:
                await ws.send_text(payload)
            except Exception as e:
                print(f"[WS ERROR] {e}")
                WEBSOCKET_CLIENTS.discard(ws)

    global ASYNC_LOOP
    if ASYNC_LOOP and ASYNC_LOOP.is_running():
        asyncio.run_coroutine_threadsafe(_send_to_all(), ASYNC_LOOP)

# ---------------- PYQT6 BACKGROUND SERVER THREAD ----------------
class RemoteServerThread(QThread):
    def __init__(self, host="0.0.0.0", port=8000):
        super().__init__()
        self.host = host
        self.port = port

    def run(self):
        import uvicorn
        import socket
        try:
            hostname = socket.gethostname()
            local_ip = [ip for ip in socket.gethostbyname_ex(hostname)[2] if not ip.startswith("192.168.56.") and not ip.startswith("127.")][0]
        except Exception:
            local_ip = "127.0.0.1"
            
        cert_file, key_file = remote_security.ensure_ssl_certificates()
        
        # Start HTTPS SSL Server on port 8443 for Unlocked Mobile Microphone Access
        if cert_file and key_file:
            def run_https():
                try:
                    uvicorn.run(app, host=self.host, port=8443, ssl_keyfile=key_file, ssl_certfile=cert_file, log_level="warning")
                except Exception as e:
                    print("[HTTPS SERVER ERROR]", e)
            
            https_thread = threading.Thread(target=run_https, daemon=True)
            https_thread.start()

        print(f"=======================================================")
        print(f"📱 INTELLIGENT AI MOBILE REMOTE OS SERVER ONLINE!")
        print(f"👉 OPEN THIS LINK ON MOBILE PHONE FOR UNBLOCKED MICROPHONE:")
        if cert_file:
            print(f"   🔒 HTTPS URL (UNLOCKED MIC): https://{local_ip}:8443/mobile")
        print(f"   🌐 HTTP URL:                 http://{local_ip}:{self.port}/mobile")
        print(f"=======================================================")
        uvicorn.run(app, host=self.host, port=self.port, log_level="warning")
