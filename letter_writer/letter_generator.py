"""
AI Letter Generator and Command Handler for JARVIS AI Assistant.
"""

import os
import json
import requests
import datetime
from pathlib import Path

try:
    from api_keys import GEMINI_API_KEY
except ImportError:
    GEMINI_API_KEY = ""

from memory import get_memory, load_memory
from .letter_intent import is_letter_command, parse_letter_intent
from .letter_types import format_letter, get_fallback_letter, CATEGORIES
from .notepad_automation import open_notepad_and_type, save_letter_file

def get_user_profile() -> dict:
    """Retrieves existing user profile information from JARVIS memory."""
    mem = load_memory()
    name = get_memory("user_name") or mem.get("name") or "Shravani" # Use saved user name or default
    return {
        "name": name,
        "college": mem.get("college") or mem.get("user_college") or "",
        "course": mem.get("course") or mem.get("user_course") or "",
        "class": mem.get("class") or mem.get("user_class") or "",
        "department": mem.get("department") or mem.get("user_department") or "",
        "email": mem.get("email") or mem.get("user_email") or "",
        "phone": mem.get("phone") or mem.get("user_phone") or "",
        "address": mem.get("address") or mem.get("user_address") or ""
    }

def check_missing_info(params: dict) -> tuple[bool, str, str]:
    """
    Checks if important information is missing and returns a prompt question if needed.
    Returns (is_missing, question, missing_field_name).
    """
    category = params.get("category")

    # Leave Application missing check
    if category in ["COLLEGE_LEAVE", "SCHOOL_LEAVE", "LEAVE", "SICK_LEAVE"]:
        if not params.get("duration"):
            return True, "How many days of leave do you need?", "duration"
        if not params.get("reason"):
            return True, "What is the reason for the leave?", "reason"

    # Job Application missing check
    elif category == "JOB_APPLICATION":
        if not params.get("role"):
            return True, "Which job role are you applying for?", "role"

    # Complaint Letter missing check
    elif category == "COMPLAINT":
        if not params.get("topic"):
            return True, "What is your complaint regarding?", "topic"

    # Bank Letter missing check
    elif category == "BANK":
        if not params.get("topic") and not params.get("reason"):
            return True, "What account issue or request do you have for the bank?", "topic"

    return False, "", ""

def generate_ai_letter(params: dict, profile: dict) -> str:
    """
    Generates a professional letter using Gemini AI or fallbacks.
    """
    category_name = CATEGORIES.get(params.get("category"), "Formal Letter")
    sender_name = profile.get("name") or "Applicant"
    receiver_title = params.get("receiver_title") or "Sir/Madam"
    org = params.get("organization") or profile.get("college") or ""
    date_str = datetime.datetime.now().strftime("%d %B %Y")

    # Build detailed context from profile
    profile_details = []
    if profile.get("college"): profile_details.append(f"College: {profile['college']}")
    if profile.get("course"): profile_details.append(f"Course: {profile['course']}")
    if profile.get("class"): profile_details.append(f"Class/Year: {profile['class']}")
    if profile.get("department"): profile_details.append(f"Department: {profile['department']}")
    if profile.get("email"): profile_details.append(f"Email: {profile['email']}")
    if profile.get("phone"): profile_details.append(f"Phone: {profile['phone']}")
    profile_str = ", ".join(profile_details) if profile_details else "Not provided"

    prompt = f"""You are a professional AI Letter Writer for JARVIS AI Assistant.
Generate a complete, highly professional, grammatically perfect, and beautifully formatted formal letter.

DETAILS:
- Letter Type: {category_name}
- Sender Name: {sender_name}
- Sender Details: {profile_str}
- Receiver Title: {receiver_title}
- Organization / Institution: {org if org else 'Respected Institution/Organization'}
- Date: {date_str}
- Duration (if applicable): {params.get('duration', 'N/A')}
- Reason / Purpose: {params.get('reason', params.get('topic', 'Formal request/representation'))}
- Job Role (if applicable): {params.get('role', 'N/A')}
- Raw User Request: {params.get('raw_command')}

CRITICAL INSTRUCTIONS:
- Write ONLY the actual letter text itself.
- Do NOT output bullet points, explanations, or compliance lists.
- Start directly with the letter content starting with Date, To, Subject, Salutation, Body, and Closing.

EXAMPLE OUTPUT FORMAT:
Date: {date_str}

To,
{receiver_title}
{org if org else 'Institution'}

Subject: {category_name} - {params.get('reason', 'Request')}

Respected {receiver_title},

[Body of letter...]

Sincerely,
{sender_name}
"""

    # 1. Try Gemini AI API
    if GEMINI_API_KEY:
        for model_name in ["gemini-flash-lite-latest", "gemini-3.5-flash", "gemini-1.5-flash"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1000}
                }
                res = requests.post(url, headers=headers, json=payload, timeout=6.0)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            text = parts[0].get("text", "").strip()
                            if text.startswith("```"):
                                lines = text.split("\n")
                                text = "\n".join([l for l in lines if not l.startswith("```")]).strip()
                            if "Subject:" in text or "Date:" in text:
                                return text
            except Exception as e:
                print(f"[GEMINI LETTER GENERATION ERROR] {model_name}: {e}")
                continue


    # 2. Try Ollama local AI fallback
    try:
        ollama_url = "http://localhost:11434/api/generate"
        res = requests.post(ollama_url, json={"model": "llama3", "prompt": prompt, "stream": False}, timeout=3.0)
        if res.status_code == 200:
            text = res.json().get("response", "").strip()
            if text:
                return text
    except Exception:
        pass

    # 3. Offline template fallback
    params["sender_name"] = sender_name
    return get_fallback_letter(params.get("category"), params)


def process_letter_command(command: str, context_state: dict = None, status_callback=None) -> str:
    """
    Main router entry point for processing letter writing commands.
    """
    if context_state is None:
        context_state = {}

    params = parse_letter_intent(command)
    profile = get_user_profile()

    # Check for pending missing information from previous turn
    pending_letter = context_state.get("pending_letter_writer")
    if pending_letter:
        field = pending_letter.get("missing_field")
        pending_params = pending_letter.get("params")
        pending_params[field] = command.strip()
        context_state["pending_letter_writer"] = None
        params = pending_params # Resume with updated details

    # Check if information is missing
    is_missing, question, missing_field = check_missing_info(params)
    if is_missing:
        context_state["pending_letter_writer"] = {
            "params": params,
            "missing_field": missing_field
        }
        return f"Sure. {question}"

    # Notify status callback if GUI available
    if status_callback:
        try:
            status_callback("AI LETTER WRITER", "Generating Letter...")
        except Exception:
            pass

    # Generate Letter
    letter_text = generate_ai_letter(params, profile)
    if not letter_text:
        return "Sorry, I could not generate the letter at this moment."

    context_state["last_generated_letter"] = letter_text

    # Open Notepad & Type automatically
    if status_callback:
        try:
            status_callback("AI LETTER WRITER", "Opening Notepad & Typing...")
        except Exception:
            pass

    success, msg = open_notepad_and_type(letter_text)

    if status_callback:
        try:
            status_callback("AI LETTER WRITER", "Completed ✓")
        except Exception:
            pass

    if success:
        return "Your letter has been written in Notepad."
    else:
        return msg
