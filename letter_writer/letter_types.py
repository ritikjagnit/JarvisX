"""
Definitions, structural formatters, and fallback templates for all 15 supported letter categories.
"""

import datetime

# Supported Categories
CATEGORIES = {
    "COLLEGE_LEAVE": "College Leave Application",
    "SCHOOL_LEAVE": "School Leave Application",
    "LEAVE": "General Leave Application",
    "SICK_LEAVE": "Sick Leave Application",
    "JOB_APPLICATION": "Job Application Letter",
    "RESIGNATION": "Resignation Letter",
    "COMPLAINT": "Formal Complaint Letter",
    "REQUEST": "Request Letter",
    "PERMISSION": "Permission Request Application",
    "APOLOGY": "Formal Apology Letter",
    "SCHOLARSHIP": "Scholarship Application",
    "BANK": "Bank Request / Complaint Letter",
    "GOVERNMENT": "Government Application / Representation",
    "BUSINESS": "Formal Business Proposal / Request",
    "PERSONAL_FORMAL": "Personal Formal Letter"
}

def format_letter(subject, body, sender_name, receiver_title="Sir/Madam", receiver_org="", date_str=None):
    """
    Standard layout formatter ensuring clean line breaks, proper spacing, and professional alignment.
    """
    if not date_str:
        date_str = datetime.datetime.now().strftime("%d %B %Y")

    receiver_block = f"To,\nThe {receiver_title}"
    if receiver_org:
        receiver_block += f"\n{receiver_org}"

    letter = f"""Date: {date_str}

{receiver_block}

Subject: {subject}

Respected {receiver_title},

{body.strip()}

Thank you for your time and consideration.

Sincerely,
{sender_name}"""
    return letter

def get_fallback_letter(category, details):
    """
    Generates structured fallback letters if online AI is unreachable.
    """
    sender = details.get("sender_name") or "Applicant"
    receiver = details.get("receiver_title") or "Sir/Madam"
    org = details.get("organization") or "Institution / Office"
    duration = details.get("duration") or "a few days"
    reason = details.get("reason") or "unavoidable personal reasons"
    date_str = datetime.datetime.now().strftime("%d %B %Y")

    if category in ["COLLEGE_LEAVE", "SCHOOL_LEAVE", "LEAVE", "SICK_LEAVE"]:
        subject = f"Application for Leave of Absence ({duration})"
        body = f"""I am writing to formally request leave of absence from {org} for a period of {duration} due to {reason}.

I will ensure that all my pending tasks and notes are caught up immediately upon my return. I kindly request you to grant me leave for the specified duration."""
        return format_letter(subject, body, sender, receiver, org, date_str)

    elif category == "JOB_APPLICATION":
        role = details.get("role") or "the advertised position"
        subject = f"Application for the Position of {role}"
        body = f"""I am writing to express my strong interest in the {role} position at {org}. With my background, technical skills, and commitment to excellence, I am confident in my ability to contribute effectively to your organization.

Enclosed with this letter are my credentials for your review. I welcome the opportunity to discuss how my qualifications align with your needs."""
        return format_letter(subject, body, sender, receiver, org, date_str)

    elif category == "RESIGNATION":
        notice = details.get("notice_period") or "standard notice period"
        subject = f"Resignation Letter - {sender}"
        body = f"""Please accept this letter as formal notification that I am resigning from my position at {org}. My decision comes after careful thought, and I intend to fulfill my {notice}.

I am extremely grateful for the opportunities provided during my tenure. I will do everything possible to ensure a smooth transition of my responsibilities."""
        return format_letter(subject, body, sender, receiver, org, date_str)

    elif category == "COMPLAINT":
        topic = details.get("topic") or "service issues"
        subject = f"Formal Complaint Regarding {topic}"
        body = f"""I am writing to bring an urgent issue regarding {topic} to your immediate attention. Despite previous attempts to resolve this, the problem persists and requires prompt administrative intervention.

I request you to look into this matter urgently and take necessary corrective measures."""
        return format_letter(subject, body, sender, receiver, org, date_str)

    elif category == "APOLOGY":
        incident = details.get("incident") or "recent oversight"
        subject = f"Formal Letter of Apology Regarding {incident}"
        body = f"""I am writing to sincerely apologize for {incident}. I deeply regret any inconvenience or confusion caused by my actions.

I assure you that I have taken measures to prevent such occurrences in the future and appreciate your understanding."""
        return format_letter(subject, body, sender, receiver, org, date_str)

    elif category == "BANK":
        issue = details.get("issue") or "account assistance"
        subject = f"Request Regarding Bank Account - {issue}"
        body = f"""I am writing to request assistance regarding my account with your branch for {issue}.

Kindly instruct the concerned department to process this request at the earliest."""
        return format_letter(subject, body, sender, receiver, org, date_str)

    # General Fallback
    subject = f"Formal Request Regarding {reason}"
    body = f"""I am writing to submit a formal representation regarding {reason} at {org}.

I request your kind consideration and look forward to a favorable response."""
    return format_letter(subject, body, sender, receiver, org, date_str)
