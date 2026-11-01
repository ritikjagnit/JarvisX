import os
import time
import subprocess
import base64
import requests
from PIL import Image
from api_keys import GEMINI_API_KEY, OPENAI_API_KEY
from voice_engine import speak

# Optional imports for local OCR engines
try:
    import easyocr
except BaseException:
    easyocr = None

try:
    import pytesseract
except BaseException as e:
    pytesseract = None

try:
    import fitz  # PyMuPDF
except BaseException as e:
    fitz = None

# Initialize easyocr reader lazily to avoid startup delay
_easyocr_reader = None

def get_easyocr_reader():
    global _easyocr_reader
    if _easyocr_reader is None and easyocr is not None:
        try:
            print("[OCR] Initializing EasyOCR Reader (English)...")
            _easyocr_reader = easyocr.Reader(['en'], gpu=False)
        except BaseException as e:
            print(f"[OCR] EasyOCR Reader initialization failed: {e}")
            _easyocr_reader = None
    return _easyocr_reader

def get_most_recent_file(extensions):
    """Finds the most recently modified file with the given extensions in Downloads, Desktop, or Documents."""
    user_home = os.path.expanduser("~")
    dirs_to_check = [
        os.path.join(user_home, "Downloads"),
        os.path.join(user_home, "Desktop"),
        os.path.join(user_home, "Documents")
    ]
    
    newest_file = None
    newest_time = 0
    
    for d in dirs_to_check:
        if not os.path.exists(d):
            continue
        try:
            for entry in os.scandir(d):
                if entry.is_file():
                    ext = os.path.splitext(entry.name)[1].lower()
                    if ext in extensions:
                        mtime = entry.stat().st_mtime
                        if mtime > newest_time:
                            newest_time = mtime
                            newest_file = entry.path
        except Exception as e:
            print(f"[OCR] Error scanning directory {d}: {e}")
            
    return newest_file

def perform_image_ocr(image_path):
    """Performs OCR on a single image using EasyOCR, Tesseract, or Gemini fallback."""
    if not os.path.exists(image_path):
        return None

    # 1. Try EasyOCR (local)
    reader = get_easyocr_reader()
    if reader is not None:
        try:
            print(f"[OCR] Running EasyOCR on: {image_path}")
            results = reader.readtext(image_path, detail=0)
            text = " ".join(results).strip()
            if text:
                return text
        except Exception as e:
            print(f"[OCR] EasyOCR failed: {e}")

    # 2. Try Pytesseract (local fallback)
    if pytesseract is not None:
        try:
            print(f"[OCR] Running Pytesseract on: {image_path}")
            text = pytesseract.image_to_string(Image.open(image_path)).strip()
            if text:
                return text
        except Exception as e:
            print(f"[OCR] Pytesseract failed: {e}")

    # 3. Try Gemini Vision (cloud fallback)
    if GEMINI_API_KEY:
        try:
            print(f"[OCR] Running Gemini Vision OCR on: {image_path}")
            with open(image_path, "rb") as f:
                img_data = f.read()
            img_b64 = base64.b64encode(img_data).decode("utf-8")
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={GEMINI_API_KEY}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{
                    "parts": [
                        {"text": "Extract all readable text from this image exactly as it appears. Output only the extracted text and nothing else."},
                        {"inlineData": {"mimeType": "image/jpeg", "data": img_b64}}
                    ]
                }]
            }
            res = requests.post(url, headers=headers, json=payload, timeout=15)
            if res.status_code == 200:
                text = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                if text:
                    return text
        except Exception as e:
            print(f"[OCR] Gemini Vision OCR failed: {e}")

    # 4. Try OpenAI Vision (cloud fallback)
    if OPENAI_API_KEY:
        try:
            print(f"[OCR] Running OpenAI Vision OCR on: {image_path}")
            with open(image_path, "rb") as f:
                img_data = f.read()
            img_b64 = base64.b64encode(img_data).decode("utf-8")
            
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract all readable text from this image exactly as it appears. Output only the extracted text and nothing else."},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                        ]
                    }
                ]
            }
            res = requests.post(url, headers=headers, json=data, timeout=15)
            if res.status_code == 200:
                text = res.json()["choices"][0]["message"]["content"].strip()
                if text:
                    return text
        except Exception as e:
            print(f"[OCR] OpenAI Vision OCR failed: {e}")

    return None

def perform_pdf_ocr(pdf_path):
    """Extracts text from PDF. Supports standard text extraction or rendering scanned pages to perform OCR."""
    if not os.path.exists(pdf_path):
        return "PDF file not found."

    if not fitz:
        return "PyMuPDF (fitz) is not installed. Unable to process PDF."

    try:
        doc = fitz.open(pdf_path)
        extracted_text_blocks = []
        total_pages = len(doc)
        
        speak(f"Processing PDF document containing {total_pages} pages...")

        for page_num in range(total_pages):
            page = doc[page_num]
            # Try native text extraction first (fast for digital PDFs)
            text = page.get_text().strip()
            
            # If native text is empty, it's a scanned PDF page. Perform image OCR
            if not text:
                print(f"[OCR] Page {page_num + 1} has no selectable text. Rendering to image for OCR...")
                pix = page.get_pixmap(dpi=150)
                temp_image_path = f"temp_page_{page_num}_{int(time.time())}.jpg"
                pix.save(temp_image_path)
                
                # Perform OCR on rendered image page
                text = perform_image_ocr(temp_image_path)
                
                # Cleanup temp file
                if os.path.exists(temp_image_path):
                    try:
                        os.remove(temp_image_path)
                    except:
                        pass
            
            if text:
                extracted_text_blocks.append(f"--- PAGE {page_num + 1} ---\n{text}\n")
                
        doc.close()
        return "\n".join(extracted_text_blocks).strip()
    except Exception as e:
        return f"Failed to extract text from PDF: {e}"

def process_ocr_command(command):
    """Processes incoming OCR intent and routes it."""
    cmd_lower = command.lower()

    # Match triggers
    is_image = "read this image" in cmd_lower or "read image" in cmd_lower
    is_pdf = "read this pdf" in cmd_lower or "read pdf" in cmd_lower

    if not is_image and not is_pdf:
        return None

    if is_image:
        speak("Searching for the most recent image on your system...")
        recent_image = get_most_recent_file([".png", ".jpg", ".jpeg"])
        if not recent_image:
            return "Shravani, I couldn't find any recent image in your Downloads, Desktop, or Documents folders."
        
        speak(f"Found image {os.path.basename(recent_image)}. Extracting text now...")
        extracted_text = perform_image_ocr(recent_image)
        
        if not extracted_text:
            return "I couldn't extract any readable text from that image."
            
    else:  # is_pdf
        speak("Searching for the most recent PDF document...")
        recent_pdf = get_most_recent_file([".pdf"])
        if not recent_pdf:
            return "Shravani, I couldn't find any recent PDF in your Downloads, Desktop, or Documents folders."

            
        speak(f"Found PDF {os.path.basename(recent_pdf)}. Processing extraction...")
        extracted_text = perform_pdf_ocr(recent_pdf)
        
        if not extracted_text:
            return "I couldn't extract any readable text from that PDF document."

    # Save to user Documents folder
    try:
        docs_dir = os.path.join(os.path.expanduser("~"), "Documents", "Jarvis_OCR_Output")
        if not os.path.exists(docs_dir):
            os.makedirs(docs_dir)
            
        filename = f"extracted_text_{int(time.time())}.txt"
        filepath = os.path.join(docs_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(extracted_text)
            
        # Open the extracted text in Notepad
        subprocess.Popen(["notepad.exe", filepath])
        
        # Read the first sentence or snippet to the user, then direct them to the opened file
        snippet = extracted_text.split("\n")[0][:100]
        if len(extracted_text) > 100:
            snippet += "..."
            
        return f"Successfully extracted text: '{snippet}'. I have opened the full text in Notepad for you."
        
    except Exception as e:
        print(f"[OCR] Save error: {e}")
        return f"Extracted text:\n\n{extracted_text}"
