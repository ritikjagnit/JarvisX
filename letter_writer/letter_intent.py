"""
Intent detection and entity extraction module for AI Letter Writer commands.
"""

import re

LETTER_TRIGGER_KEYWORDS = [
    "write a letter", "write letter", "write application", "write a leave application",
    "write leave application", "write sick leave", "write a sick leave",
    "write job application", "write a job application", "write resignation",
    "write a resignation", "write complaint", "write a complaint",
    "write request letter", "write a request letter", "write apology",
    "write an apology", "write scholarship", "write a scholarship",
    "write letter to", "write application for", "letter writer", "open letter writer",
    "write this letter", "type letter", "draft a letter", "draft letter",
    "application for fee concession", "letter requesting permission",
    "application for leave", "leave application for college", "leave application for school"
]

def is_letter_command(command: str) -> bool:
    """Checks if input voice command is related to writing a letter or application."""
    if not command:
        return False
    cmd_lower = command.lower().strip()
    if any(keyword in cmd_lower for keyword in LETTER_TRIGGER_KEYWORDS):
        return True

    # Flexible natural language detection
    if ("write" in cmd_lower or "draft" in cmd_lower or "type" in cmd_lower) and (
        "letter" in cmd_lower or "application" in cmd_lower or "leave" in cmd_lower or "resignation" in cmd_lower or "complaint" in cmd_lower or "apology" in cmd_lower
    ):
        return True

    if "application for" in cmd_lower or "letter to" in cmd_lower or "letter requesting" in cmd_lower:
        return True

    return False

def parse_letter_intent(command: str) -> dict:
    """
    Parses command intent and extracts parameters (category, duration, reason, receiver, role, topic).
    """
    cmd = command.lower().strip()

    # Default structure
    parsed = {
        "raw_command": command,
        "intent": "LETTER_WRITE",
        "category": "PERSONAL_FORMAL",
        "receiver_title": "Sir/Madam",
        "organization": "",
        "duration": "",
        "reason": "",
        "role": "",
        "topic": "",
        "explicit_notepad": "notepad" in cmd or "type" in cmd
    }

    # Extract Receiver
    if "principal" in cmd:
        parsed["receiver_title"] = "Principal"
        parsed["organization"] = "College / School"
    elif "manager" in cmd:
        parsed["receiver_title"] = "Manager"
    elif "hod" in cmd or "head of department" in cmd:
        parsed["receiver_title"] = "Head of Department (HOD)"
    elif "bank" in cmd:
        parsed["receiver_title"] = "Branch Manager"
        parsed["organization"] = "Bank"

    # Extract Duration (e.g., 2 days, 3 days, 1 week)
    duration_match = re.search(r'(\d+|\b(one|two|three|four|five)\b)\s*(days|day|weeks|week)', cmd)
    if duration_match:
        parsed["duration"] = duration_match.group(0)


    # Extract Reason / Topic hints
    if "sick" in cmd or "fever" in cmd or "medical" in cmd:
        parsed["reason"] = "medical reasons / ill health"
    elif "fee concession" in cmd or "concession" in cmd:
        parsed["reason"] = "fee concession request"

    # Category Detection
    if "sick leave" in cmd or ("sick" in cmd and "leave" in cmd):
        parsed["intent"] = "LETTER_LEAVE"
        parsed["category"] = "SICK_LEAVE"
    elif "college" in cmd and "leave" in cmd:
        parsed["intent"] = "LETTER_LEAVE"
        parsed["category"] = "COLLEGE_LEAVE"
        parsed["receiver_title"] = parsed["receiver_title"] if parsed["receiver_title"] != "Sir/Madam" else "Principal"
    elif "school" in cmd and "leave" in cmd:
        parsed["intent"] = "LETTER_LEAVE"
        parsed["category"] = "SCHOOL_LEAVE"
        parsed["receiver_title"] = "Principal"
    elif "leave" in cmd:
        parsed["intent"] = "LETTER_LEAVE"
        parsed["category"] = "LEAVE"
    elif "job" in cmd or "job application" in cmd:
        parsed["intent"] = "LETTER_JOB_APPLICATION"
        parsed["category"] = "JOB_APPLICATION"
        # Try to extract role e.g. job application for software developer
        role_match = re.search(r'job application (for|as)?\s*([a-zA-Z\s]+)', cmd)
        if role_match and role_match.group(2):
            parsed["role"] = role_match.group(2).strip()
    elif "resignation" in cmd or "resign" in cmd:
        parsed["intent"] = "LETTER_RESIGNATION"
        parsed["category"] = "RESIGNATION"
    elif "complaint" in cmd:
        parsed["intent"] = "LETTER_COMPLAINT"
        parsed["category"] = "COMPLAINT"
        # Try to extract complaint topic
        topic_match = re.search(r'complaint (letter|about|regarding)?\s*([a-zA-Z\s]+)', cmd)
        if topic_match and topic_match.group(2):
            parsed["topic"] = topic_match.group(2).strip()
    elif "apology" in cmd or "sorry" in cmd:
        parsed["intent"] = "LETTER_APOLOGY"
        parsed["category"] = "APOLOGY"
    elif "scholarship" in cmd:
        parsed["intent"] = "LETTER_APPLICATION"
        parsed["category"] = "SCHOLARSHIP"
    elif "bank" in cmd:
        parsed["intent"] = "LETTER_REQUEST"
        parsed["category"] = "BANK"
    elif "permission" in cmd:
        parsed["intent"] = "LETTER_REQUEST"
        parsed["category"] = "PERMISSION"
    elif "request" in cmd:
        parsed["intent"] = "LETTER_REQUEST"
        parsed["category"] = "REQUEST"
    elif "invitation" in cmd:
        parsed["intent"] = "LETTER_INVITATION"
        parsed["category"] = "BUSINESS"
    elif "application" in cmd:
        parsed["intent"] = "LETTER_APPLICATION"
        parsed["category"] = "COLLEGE_LEAVE" if "college" in cmd else "LEAVE"

    return parsed
