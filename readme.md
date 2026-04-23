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
