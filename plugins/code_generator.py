import os
import subprocess
import requests
import time
from voice_engine import speak

try:
    from api_keys import OPENAI_API_KEY
except ImportError:
    OPENAI_API_KEY = ""

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

    if not OPENAI_API_KEY:
        return "I need an OpenAI API key to generate code, Boss."

    speak("Sure, let me generate that code for you...")

    # Refine prompt for OpenAI
    prompt = f"Write the code for {command}. Only provide the code, no explanation, no markdown backticks."

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
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            return "Failed to connect to AI server."

        result = response.json()
        code_content = result["choices"][0]["message"]["content"]

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
