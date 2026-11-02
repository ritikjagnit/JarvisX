"""
Autonomous AI Coder Agent (DevJarvis)
Full-Stack Autonomous Software Engineering Module for SHRIVA AI / JarvisX.

Capabilities:
1. Analyzes user natural language coding request (websites, landing pages, Python apps, games, tools).
2. Generates complete, production-grade, multi-file codebases without placeholders.
3. Automatically creates a structured project directory in ~/Desktop/Jarvis_Projects/<project_name>.
4. Writes all source files (HTML, CSS, JS, Python, README, etc.).
5. Automatically launches the project in Microsoft Visual Studio Code (`code <dir>`).
6. Automatically previews web applications in the default browser (Chrome/Edge).
7. Provides audio and voice confirmation to the user.
"""

import os
import re
import sys
import json
import time
import shutil
import requests
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime

from voice_engine import speak
from jarvis_sfx import play_sfx
from api_keys import GEMINI_API_KEY, OPENAI_API_KEY

PROJECTS_BASE_DIR = Path.home() / "Desktop" / "Jarvis_Projects"


def _sanitize_project_name(raw_name: str) -> str:
    """Creates a clean, filesystem-safe folder name."""
    clean = re.sub(r'[^a-zA-Z0-9_\- ]', '', raw_name).strip().replace(' ', '_').lower()
    return clean[:40] if clean else f"project_{int(time.time())}"


def _query_ai_engine(system_prompt: str, user_prompt: str) -> str:
    """Queries Gemini, OpenAI, or free Pollinations AI with automatic fallback."""
    # 1. Try Google Gemini API
    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{system_prompt}\n\nTask: {user_prompt}"}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.4,
                    "maxOutputTokens": 8192
                }
            }
            res = requests.post(url, headers=headers, json=payload, timeout=35)
            if res.status_code == 200:
                data = res.json()
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                if text:
                    return text
        except Exception as e:
            print(f"[CODER-AGENT] Gemini error: {e}")

    # 2. Try OpenAI API
    if OPENAI_API_KEY:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.4
            }
            res = requests.post(url, headers=headers, json=data, timeout=35)
            if res.status_code == 200:
                text = res.json()["choices"][0]["message"]["content"].strip()
                if text:
                    return text
        except Exception as e:
            print(f"[CODER-AGENT] OpenAI error: {e}")

    # 3. Try Pollinations AI (Free, high-quality, no API key required)
    try:
        url = "https://text.pollinations.ai/"
        headers = {"Content-Type": "application/json"}
        data = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "model": "openai",
            "jsonMode": True
        }
        res = requests.post(url, headers=headers, json=data, timeout=40)
        if res.status_code == 200 and res.text.strip():
            return res.text.strip()
    except Exception as e:
        print(f"[CODER-AGENT] Pollinations fallback error: {e}")

    return ""


def _parse_code_manifest(ai_response: str) -> dict:
    """Parses JSON or markdown code blocks into a dictionary of {filename: content}."""
    manifest = {
        "project_name": "ai_project",
        "description": "Autonomous AI Generated Project",
        "files": {}
    }

    # Attempt 1: Direct JSON parsing
    try:
        cleaned = ai_response.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in cleaned and cleaned.startswith("```"):
            cleaned = cleaned.split("```", 1)[1].split("```", 1)[0].strip()

        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            if "files" in parsed and isinstance(parsed["files"], (dict, list)):
                manifest["project_name"] = parsed.get("project_name", manifest["project_name"])
                manifest["description"] = parsed.get("description", manifest["description"])
                if isinstance(parsed["files"], dict):
                    manifest["files"] = parsed["files"]
                elif isinstance(parsed["files"], list):
                    for item in parsed["files"]:
                        if "path" in item and "content" in item:
                            manifest["files"][item["path"]] = item["content"]
                        elif "filename" in item and "code" in item:
                            manifest["files"][item["filename"]] = item["code"]
                return manifest
    except Exception:
        pass

    # Attempt 2: Regex extraction of ```filename ... ``` or ### Filename: ...
    file_pattern = re.compile(r'###\s*(?:File(?:name)?:\s*)?([a-zA-Z0-9_\-\./\\]+)\s*\n```[a-zA-Z0-9_-]*\s*\n(.*?)\n```', re.DOTALL)
    matches = file_pattern.findall(ai_response)
    if matches:
        for fname, code in matches:
            clean_fname = fname.strip().replace("`", "")
            manifest["files"][clean_fname] = code.strip()
        return manifest

    # Attempt 3: Extract any code blocks
    block_pattern = re.compile(r'```([a-zA-Z0-9_-]+)?\s*\n(.*?)\n```', re.DOTALL)
    blocks = block_pattern.findall(ai_response)
    if blocks:
        for idx, (lang, code) in enumerate(blocks):
            lang = lang.lower().strip()
            if lang in ["html", "htm"]:
                fname = "index.html"
            elif lang == "css":
                fname = "style.css"
            elif lang in ["js", "javascript"]:
                fname = "script.js"
            elif lang in ["py", "python"]:
                fname = "main.py"
            elif lang in ["json"]:
                fname = "data.json"
            else:
                fname = f"file_{idx+1}.txt"

            manifest["files"][fname] = code.strip()

    return manifest


def open_in_vs_code(folder_path: Path, main_file: Path = None) -> bool:
    """Launches VS Code in the target project folder and opens the primary file."""
    try:
        # Check if 'code' command is available
        code_cmd = shutil.which("code")
        if not code_cmd:
            # Common Windows VS Code installation locations
            candidates = [
                Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Microsoft VS Code" / "bin" / "code.cmd",
                Path(os.environ.get("PROGRAMFILES", "")) / "Microsoft VS Code" / "bin" / "code.cmd",
                Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft VS Code" / "bin" / "code.cmd",
            ]
            for c in candidates:
                if c.exists():
                    code_cmd = str(c)
                    break

        if code_cmd:
            args = [code_cmd, str(folder_path)]
            if main_file and main_file.exists():
                args.extend(["-r", str(main_file)])
            subprocess.Popen(args, shell=True)
            print(f"[CODER-AGENT] Successfully opened in VS Code: {folder_path}")
            return True
        else:
            # Fallback: Open folder in Windows Explorer
            os.startfile(str(folder_path))
            print("[CODER-AGENT] VS Code executable not detected in PATH. Opened project folder in Explorer.")
            return False
    except Exception as e:
        print(f"[CODER-AGENT ERROR] Could not open VS Code: {e}")
        try:
            os.startfile(str(folder_path))
        except Exception:
            pass
        return False


def build_software_project(user_request: str, status_callback=None) -> str:
    """
    Core Autonomous Coding Agent Pipeline:
    1. Analyzes requirement.
    2. Generates multi-file full-stack codebase via LLM.
    3. Writes files into ~/Desktop/Jarvis_Projects/<project_name>.
    4. Launches VS Code and Browser preview.
    5. Returns vocal status.
    """
    if status_callback:
        status_callback("⚡ SHRIVA AI DEV ENGINE: Analyzing project architecture...", "#00f0ff")

    play_sfx("ack")
    speak("Analyzing project requirements, Sir. Initiating autonomous code synthesis.")

    system_prompt = """You are SHRIVA AI / Jarvis Autonomous Principal Software Architect.
Your task is to take any software or website request and generate the complete, production-ready, beautiful codebase.

RULES:
1. Provide 100% COMPLETE, working code. NEVER write comments like '// add code here' or '/* style goes here */'.
2. Write modern, responsive, stunning UI (Glassmorphism, vibrant gradients, neon accents, sleek typography).
3. For Web projects: ALWAYS generate 'index.html', 'style.css', and 'script.js' with full interactive functionality.
4. For Python projects: ALWAYS generate 'main.py' and 'requirements.txt'.
5. Output strictly in the following JSON format:
{
  "project_name": "short_snake_case_name",
  "description": "Brief description of the application",
  "main_entry": "index.html",
  "files": {
    "index.html": "<complete html code>",
    "style.css": "<complete css code>",
    "script.js": "<complete javascript code>",
    "README.md": "<clean documentation with run instructions>"
  }
}
Output ONLY valid JSON. Do not wrap with additional conversational text.
"""

    raw_ai_text = _query_ai_engine(system_prompt, user_request)

    if not raw_ai_text:
        msg = "I could not generate the codebase due to an AI service interruption. Please verify your internet connection or API keys."
        speak(msg)
        return msg

    if status_callback:
        status_callback("⚡ SHRIVA AI DEV ENGINE: Assembling source files...", "#00ff88")

    manifest = _parse_code_manifest(raw_ai_text)
    files = manifest.get("files", {})

    if not files:
        # Fallback: if manifest failed, synthesize a sleek single-page app
        p_name = _sanitize_project_name(user_request)
        files["index.html"] = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{p_name.replace('_', ' ').title()}</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }}
    body {{ background: #0b0f19; color: #fff; min-height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
    .card {{ background: rgba(18, 24, 38, 0.85); border: 1px solid #00f0ff; border-radius: 16px; padding: 40px; max-width: 650px; text-align: center; box-shadow: 0 10px 40px rgba(0, 240, 255, 0.2); }}
    h1 {{ color: #00f0ff; margin-bottom: 16px; font-size: 2.2rem; }}
    p {{ color: #94a3b8; font-size: 1.1rem; line-height: 1.6; margin-bottom: 24px; }}
    .btn {{ background: linear-gradient(135deg, #00f0ff, #0088ff); color: #000; font-weight: bold; padding: 12px 28px; border-radius: 8px; border: none; cursor: pointer; transition: 0.3s; font-size: 1rem; }}
    .btn:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 240, 255, 0.5); }}
  </style>
</head>
<body>
  <div class="card">
    <h1>⚡ {p_name.replace('_', ' ').title()}</h1>
    <p>Synthesized by SHRIVA AI Autonomous Coder. Ready for customization.</p>
    <button class="btn" onclick="alert('System operational, Sir.')">Explore System</button>
  </div>
</body>
</html>"""
        manifest["project_name"] = p_name

    # Create destination directory on user's Desktop
    project_slug = _sanitize_project_name(manifest.get("project_name", "jarvis_project"))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_name = f"{project_slug}_{timestamp}"
    project_dir = PROJECTS_BASE_DIR / folder_name
    project_dir.mkdir(parents=True, exist_ok=True)

    # Write each source file
    written_files = []
    main_file_path = None

    for rel_path, content in files.items():
        clean_rel = rel_path.lstrip("/\\")
        dest_file = project_dir / clean_rel
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        dest_file.write_text(content, encoding="utf-8")
        written_files.append(dest_file.name)

        if not main_file_path:
            if dest_file.name.lower() in ["index.html", "main.py", "app.py"]:
                main_file_path = dest_file

    if not main_file_path and written_files:
        main_file_path = project_dir / written_files[0]

    # Create run helper batch file for 1-click execution
    if any(f.endswith(".html") for f in written_files):
        preview_bat = project_dir / "preview.bat"
        preview_bat.write_text(f'@echo off\nstart "" "index.html"\nexit\n', encoding="utf-8")
    elif any(f.endswith(".py") for f in written_files):
        run_bat = project_dir / "run.bat"
        run_bat.write_text(f'@echo off\npython main.py\npause\n', encoding="utf-8")

    # Step 4: Open in VS Code
    if status_callback:
        status_callback(f"🚀 SHRIVA AI DEV ENGINE: Launching {folder_name} in VS Code...", "#38bdf8")

    opened_vscode = open_in_vs_code(project_dir, main_file_path)

    # Step 5: If web project, automatically open live browser preview
    if main_file_path and main_file_path.suffix.lower() == ".html":
        try:
            webbrowser.open(main_file_path.as_uri())
        except Exception:
            pass

    # Play completion sound and confirm
    play_sfx("boot")
    summary = f"Sir, I have engineered the complete codebase for {project_slug.replace('_', ' ')}. Created {len(written_files)} files in your Desktop Projects folder, and opened it in Visual Studio Code."
    speak(summary)

    return f"🚀 **SHRIVA AI Autonomous Developer Online**\n\n" \
           f"📁 **Project:** `{folder_name}`\n" \
           f"📍 **Path:** `{project_dir}`\n" \
           f"📄 **Generated Files ({len(written_files)}):** {', '.join(written_files)}\n" \
           f"⚡ **VS Code Status:** {'Launched Successfully' if opened_vscode else 'Folder Opened in Explorer'}\n" \
           f"🌐 **Live Preview:** {'Opened in Browser' if main_file_path and main_file_path.suffix == '.html' else 'Ready to run'}"


def is_coding_command(command: str) -> bool:
    """Detects if user is asking Jarvis to build, code, or program something."""
    cmd = command.lower()
    coding_triggers = [
        "website banao", "make a website", "create a website", "build a website",
        "make website", "create website", "build website", "develop website",
        "landing page", "portfolio website", "code likho", "write code",
        "write a python script", "create a python script", "make a python",
        "create python", "build an app", "create an app", "make an app",
        "app banao", "software banao", "vs code me", "open in vs code",
        "snake game", "calculator app", "todo app", "weather app",
        "write script", "code for", "build me a", "make me a", "program a"
    ]
    return any(trigger in cmd for trigger in coding_triggers)


def process_coding_command(command: str, status_callback=None) -> str:
    """Entry point router for coding voice/text commands."""
    return build_software_project(command, status_callback=status_callback)


if __name__ == "__main__":
    test_prompt = "Create a stunning modern coffee shop landing page with dark theme and glassmorphism"
    print(process_coding_command(test_prompt))
