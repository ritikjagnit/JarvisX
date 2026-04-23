# JARVIS-PY 🚀  
### The Ultimate AI Desktop Assistant  

JARVIS-PY is a premium, high-performance voice-activated AI assistant designed to take full control of your Windows environment. Built with a focus on speed, aesthetics, and multitasking, it features a custom PyQt6 dashboard with modern glassmorphism and interactive animations.

---

## ✨ Key Features

- **🎙️ Voice & Text Intelligence**: High-accuracy speech recognition (Google/Vosk) and responsive text commands.
- **🚥 Priority Command Queue**: Advanced multitasking system that handles multiple requests simultaneously without blocking the UI.
- **🖥️ System Automation**: Launch applications, close processes, perform system-wide scans, and monitor metrics with simple voice commands.
- **🌐 Deep Search Integration**: Integrated web search and browser control via `browser_control.py`.
- **🛡️ Privacy & Security**: Local audit logging with AES encryption and privacy-focused data management.
- **🎨 Premium UI/UX**: State-of-the-art PyQt6 dashboard featuring a slick "Iron Man" inspired aesthetic, dynamic terminal output, and micro-animations.

---

## 🛠️ Tech Stack

- **Core**: Python 3.x
- **UI Framework**: PyQt6 (Custom implementation)
- **Speech Processing**: SpeechRecognition, Pyttsx3, SoundDevice, Vosk
- **AI Backend**: OpenAI GPT-3.5/4 Integration
- **Automation**: PyAutoGUI, OS-level hooks
- **Security**: Cryptography (Fernet)

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have Python 3.10+ installed. It is recommended to use a virtual environment.

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/your-repo/jarvis_py.git
cd jarvis_py

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Copy `.env.example` to `.env` and add your local keys there. Never commit real API keys.
```bash
OPENAI_API_KEY=your_openai_api_key_here
POLLINATIONS_API_KEY=
WOLFRAM_ALPHA_APP_ID=
```

### 4. Run Jarvis
```bash
python main.py
```

---

## Render Deployment

JarvisX is primarily a Windows desktop assistant. Render runs Linux web services,
so the hosted version uses `render_app.py` as a lightweight public status page
and health-check service. Desktop-only features such as PyQt UI, microphone
input, text-to-speech, and system automation should be run locally with
`python main.py`.

### Option A: Deploy with Blueprint
1. Push this repository to GitHub.
2. In Render, create a new Blueprint and select this repository.
3. Render will read `render.yaml`.
4. Add secret values in Render's Environment panel, not in source code.

### Option B: Deploy as a Web Service
Use these settings in Render:

```text
Runtime: Python
Build Command: pip install -r requirements-render.txt
Start Command: python render_app.py
Health Check Path: /healthz
```

Optional environment variables:

```text
OPENAI_API_KEY
POLLINATIONS_API_KEY
WOLFRAM_ALPHA_APP_ID
```

---

## 📖 Usage Guide

- **Voice Command**: Click the **"Voice Command"** button to toggle continuous listening. Jarvis will respond to your queries and execute system tasks.
- **Terminal Input**: Type commands directly into the input box at the bottom for silent operation.
- **Dashboard Buttons**:
    - **Scan**: Run system diagnostics.
    - **Security**: Perform a security audit.
    - **Analytics**: View real-time system metrics.
    - **Settings**: Open configuration menu.

---

## 📂 Project Structure

- `main.py`: Entry point for the application and UI bridge.
- `command_engine.py`: Logic for processing and prioritizing commands.
- `voice_engine.py`: Handles Text-to-Speech (TTS) and voice input.
- `ui/`: Contains the PyQt6 visual components.
- `privacy_manager.py`: Manages encrypted audit logs and user data.
- `system_control.py`: OS-level integrations for app and file management.

---

## 📝 License
This project is licensed under the MIT License.

---
*Built with ❤️ by the Ritik Jagnit*
