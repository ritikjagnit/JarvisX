import os
import time
import glob
import threading
from voice_engine import speak

NOTES_DIR = "jarvis_data/notes"
if not os.path.exists(NOTES_DIR): os.makedirs(NOTES_DIR)

def save_note(text):
    filename = os.path.join(NOTES_DIR, f"note_{int(time.time())}.txt")
    with open(filename, "w", encoding='utf-8') as f:
        f.write(text)
    print(f"[DEBUG-NOTES] Content permanently written to {filename}")
    return "Note saved successfully."

def trigger_reminder(message, seconds):
    time.sleep(seconds)
    print(f"\n[DEBUG-REMINDER] Executing reminder event: {message}")
    speak(f"Reminder Alert Boss! {message}")

def process_notes_command(command):
    # Reminder feature (Background Thread Wait)
    # E.g. "remind me in 10 seconds to drink water"
    if "remind me" in command:
        print(f"[DEBUG-NOTES] Reminder framework triggered: {command}")
        try:
            if "seconds" in command:
                parts = command.split("seconds")
                time_part = parts[0].split()[-1] # extraction 
                seconds = int(time_part)
                
                # Getting task payload
                message = parts[1].replace("to ", "", 1).strip() if len(parts) > 1 and parts[1].strip() else "Time is up!"
                
                # Spinning off non-blocking alert thread
                threading.Thread(target=trigger_reminder, args=(message, seconds), daemon=True).start()
                return f"Reminder securely set for {seconds} seconds."
        except Exception as e:
            print(f"[DEBUG-NOTES] Reminder parsing error: {e}")
            return "Failed to set reminder. Ensure format matches: remind me in 10 seconds."

    # Note creation
    for trigger in ["take a note", "save a note", "record a note", "write a note", "note likho"]:
        if trigger in command:
            print(f"[DEBUG-NOTES] Write protocol initiated")
            content = command.split(trigger)[-1].strip()
            if not content: return "What string should I save into the note?"
            return save_note(content)

    # Note read
    if "read my notes" in command or "show my notes" in command:
        files = glob.glob(os.path.join(NOTES_DIR, "*.txt"))
        if not files: return "You have no saved notes."
        latest = max(files, key=os.path.getctime)
        with open(latest, 'r', encoding='utf-8') as f:
            last_note = f.read()
            
        print(f"[DEBUG-NOTES] Displaying latest notebook artifact")
        return f"You have {len(files)} notes spanning your history. Your most recent entry says: {last_note}"

    return None
