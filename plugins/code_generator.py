import os
import subprocess
import requests
import time
from voice_engine import speak

try:
    from api_keys import OPENAI_API_KEY, GEMINI_API_KEY
except ImportError:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

def process_code_command(command):
    cmd_lower = command.lower()
    
    # Check if user wants code
    code_triggers = ["code", "program", "script", "logic", "bnado", "likho", "likh do", "likh"]
    if not any(trigger in cmd_lower for trigger in code_triggers):
        return None
    
    # Check if user wants to generate something
    generate_triggers = ["generate", "write", "create", "make", "want", "chahiye", "dedo"]
    if not any(trigger in cmd_lower for trigger in generate_triggers):
        return None

    speak("Sure, let me generate that code for you...")

    # Refine prompt
    prompt = f"Write the code for {command}. Only provide the code, no explanation, no markdown backticks."

    code_content = None

    # 1. Try Gemini
    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={GEMINI_API_KEY}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            res = requests.post(url, headers=headers, json=payload, timeout=10)
            if res.status_code == 200:
                code_content = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                # Clean up any potential markdown code blocks wrapped around the text
                if code_content.startswith("```"):
                    lines = code_content.splitlines()
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    code_content = "\n".join(lines).strip()
        except Exception as e:
            print(f"[CODE GEN GEMINI ERROR] {e}")

    # 2. Try OpenAI
    if not code_content and OPENAI_API_KEY:
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": "You are a senior developer. Output only raw code."},
                    {"role": "user", "content": prompt}
                ]
            }
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                code_content = result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"[CODE GEN OPENAI ERROR] {e}")

    # 3. Try Pollinations (Free Fail-safe Backup)
    if not code_content:
        try:
            url = "https://text.pollinations.ai/"
            headers = {"Content-Type": "application/json"}
            data = {
                "messages": [
                    {"role": "system", "content": "You are a senior developer. Output only raw code. No markdown backticks."},
                    {"role": "user", "content": prompt}
                ]
            }
            res = requests.post(url, headers=headers, json=data, timeout=10)
            if res.status_code == 200:
                code_content = res.text.strip()
        except Exception as e:
            print(f"[CODE GEN POLLINATIONS ERROR] {e}")

    if not code_content:
        return "Something went wrong while generating the code. Please check your internet connection."

    try:
        # Determine extension
        ext = "txt"
        if "html" in cmd_lower: ext = "html"
        elif "python" in cmd_lower or ".py" in cmd_lower: ext = "py"
        elif "javascript" in cmd_lower or "js" in cmd_lower: ext = "js"
        elif "css" in cmd_lower: ext = "css"
        elif "java" in cmd_lower: ext = "java"
        elif "cpp" in cmd_lower or "c++" in cmd_lower: ext = "cpp"
        elif "react" in cmd_lower: ext = "jsx"
        
        # Save to file
        save_dir = os.path.join(os.path.expanduser("~"), "Documents", "Jarvis_Generated_Code")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        filename = f"generated_code_{int(time.time())}.{ext}"
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code_content)
            
        speak(f"Code generated successfully. Opening it in VS Code.")
        
        # Open in VS Code
        try:
            subprocess.Popen(["code", filepath], shell=True)
        except Exception as e:
            # Fallback to notepad
            subprocess.Popen(["notepad.exe", filepath])
            return f"Generated code, but couldn't find VS Code. Opened in Notepad instead."

        return f"I have generated the {ext} code and opened it in VS Code for you."

    except Exception as e:
        print(f"[CODE GEN ERROR] {e}")
        return "Something went wrong while generating the code."
