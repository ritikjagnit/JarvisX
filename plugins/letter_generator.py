import os
import time
import random
import datetime
import pyautogui

# ---------------- FORMATS ---------------- #

def format_email(subject, body, sender, receiver):
    return f"""To: {receiver}
Subject: {subject}

{body}

Regards,
{sender}
"""

def format_application(subject, body, sender, receiver, date):
    return f"""Date: {date}

To,
{receiver}

Subject: {subject}

{body}

Sincerely,
{sender}
"""

def format_love_letter(body, sender):
    return f"""{body}

Forever yours,
{sender}
"""

# ---------------- EXTRA LINES ---------------- #

EXTRA_LINES = [
    "I truly appreciate you being in my life.",
    "You mean everything to me.",
    "Thank you for being my strength.",
    "I feel lucky to have you."
]

# ---------------- CONTENT ENGINE ---------------- #

def generate_body(letter_type, tone, receiver):

    if letter_type == "love":
        return f"""My dearest {receiver},

From the moment you came into my life, everything changed in the most beautiful way. You are not just someone I love, you are my happiness, my peace, and my strength.

Every time I see you smile, it makes my entire day better. Your presence alone gives me comfort and confidence. Life feels incomplete without you, and I truly cannot imagine a future without you in it.

No matter what happens, I promise to stand by your side, support you, and love you endlessly."""

    elif letter_type == "leave":
        return f"""I hope this message finds you well.

I am writing to formally request leave due to personal reasons that require my immediate attention. I assure you that I will complete all my responsibilities and resume my duties as soon as possible.

I sincerely apologize for any inconvenience caused and appreciate your understanding."""

    elif letter_type == "holiday":
        return f"""I hope you are doing well.

Wishing you a joyful and peaceful holiday season. May this time bring happiness, relaxation, and positivity into your life.

Enjoy your holidays and take care."""

    return "Content not available."

# ---------------- MAIN ENGINE ---------------- #

def generate_letter(command, user_name="Ritik", receiver_name="Sir/Madam"):

    command = command.lower()
    date_str = datetime.datetime.now().strftime("%d %B %Y")

    # Detect type
    if "love" in command:
        letter_type = "love"
    elif "leave" in command:
        letter_type = "leave"
    elif "holiday" in command:
        letter_type = "holiday"
    else:
        print("❌ Unknown letter type")
        return

    # Generate body
    body = generate_body(letter_type, "normal", receiver_name)
    body += "\n\n" + random.choice(EXTRA_LINES)

    # 🔥 FORMAT FIX LOGIC

    if letter_type == "love":
        # ❌ NEVER email/application
        final_text = format_love_letter(body, user_name)

    elif letter_type == "leave":
        if "email" in command:
            final_text = format_email("Leave Request", body, user_name, receiver_name)
        else:
            final_text = format_application("Leave Application", body, user_name, receiver_name, date_str)

    elif letter_type == "holiday":
        final_text = format_email("Holiday Wishes", body, user_name, receiver_name)

    # Open Notepad
    os.system("start notepad")
    time.sleep(2)

    # Type
    pyautogui.write(final_text, interval=0.01)

    print("✅ Done")

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    generate_letter("write love letter")