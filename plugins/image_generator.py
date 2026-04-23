import webbrowser
import os
import requests
import time
from urllib.parse import quote
from voice_engine import speak

try:
    from api_keys import POLLINATIONS_API_KEY
except ImportError:
    POLLINATIONS_API_KEY = ""

def process_image_command(command):
    # Normalize command
    cmd_lower = command.lower()
    
    # Check if this is an image generation intent
    image_keywords = ["generate", "image", "draw", "make", "create", "photo", "picture", "dikhao", "banao"]
    if not any(kw in cmd_lower for kw in image_keywords):
        return None
    
    # Specific exclusionary checks (e.g., "make a note" is not an image, "generate code" is not an image)
    if any(ex in cmd_lower for ex in ["note", "file", "folder", "code", "program", "script", "logic"]):
        return None

    # Extract prompt: remove common keywords
    prompt = cmd_lower
    for kw in ["generate", "image", "draw", "make", "create", "photo", "picture", "kr do", "dikhao", "banao", "an", "a"]:
        prompt = prompt.replace(kw, "")
    prompt = prompt.strip()

    if not prompt:
        speak("What image should I generate, Boss?")
        return "Please specify an image prompt."

    response = f"Generating and downloading image for {prompt}. Please wait..."
    speak(response)
    
    # Using Pollinations.ai (Flux model)
    import random
    seed = random.randint(1, 1000000)
    image_url = f"https://pollinations.ai/p/{quote(prompt)}?width=1080&height=1080&seed={seed}&model=flux"
    
    try:
        # Simulate a real browser request to avoid being blocked or getting low-quality/corrupted data
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # Download the image with a timeout
        res = requests.get(image_url, headers=headers, timeout=30)
        
        if res.status_code != 200:
            raise Exception(f"Server returned status {res.status_code}")
            
        img_data = res.content
        
        # Simple check if it's actually an image (JPEG/PNG/etc)
        if len(img_data) < 1000: # Files too small are likely error messages or corrupted
             raise Exception("Generated data is too small to be a valid image.")

        # Create directory
        save_dir = os.path.join(os.path.expanduser("~"), "Documents", "Jarvis_Generated_Images")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        filename = f"image_{int(time.time())}.jpg"
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(img_data)
            
        # Ensure file is completely written before opening
        time.sleep(1)
        
        # Open the image locally
        os.startfile(filepath)
        
        return f"I have generated and saved the image for {prompt} in your Documents folder."
        
    except Exception as e:
        print(f"[IMAGE ERROR] {e}")
        # Fallback to browser if download fails
        webbrowser.open(image_url)
        return f"I generated the image but couldn't download it. Opening it in your browser instead."
