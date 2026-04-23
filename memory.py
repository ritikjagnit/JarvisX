import json
import os

MEMORY_DIR = "jarvis_data"
MEMORY_FILE = os.path.join(MEMORY_DIR, "memory.json")

if not os.path.exists(MEMORY_DIR): os.makedirs(MEMORY_DIR)

def load_memory():
    if not os.path.exists(MEMORY_FILE): return {}
    with open(MEMORY_FILE, "r") as f:
        try: return json.load(f)
        except: return {}

def save_memory_db(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_memory(key, value):
    mem = load_memory()
    mem[key.lower()] = value
    save_memory_db(mem)
    print(f"[DEBUG-MEMORY] Saved directly to database -> {key}: {value}")

def get_memory(key):
    mem = load_memory()
    return mem.get(key.lower(), None)


def process_memory_command(command, context_state):
    """
    CONFIRMATION-BASED MEMORY SYSTEM
    Uses active context state from Brain Router to gatekeep saves securely.
    """
    pending = context_state.get("pending_memory")
    
    # Check if we are currently waiting for user confirmation
    if pending:
        confirm_words = ["yes", "save it", "got it", "yup", "sure", "ok", "okay", "yeah"]
        reject_words = ["no", "cancel", "ignore", "nevermind", "nope", "stop"]
        
        if any(word == command for word in confirm_words):
            if pending["type"] == "user_name":
                save_memory("user_name", pending["value"])
                context_state["pending_memory"] = None
                return f"Got it, I will permanently remember that your name is {pending['value']}."
                
            elif pending["type"] == "general_fact":
                mem = load_memory()
                facts = mem.get("general_facts", [])
                facts.append(pending["value"])
                mem["general_facts"] = facts
                save_memory_db(mem)
                context_state["pending_memory"] = None
                return "Saved successfully. I've updated my database."
                
        elif any(word == command for word in reject_words):
            context_state["pending_memory"] = None
            return "Okay, I've cancelled the save request."
            
        else:
            # If the user ignores the prompt and asks something else entirely, discard the pending state
            context_state["pending_memory"] = None

    # New Storage Triggers -> Gathers data but triggers confirmation instead of instantly saving
    if "my name is" in command:
        name = command.split("my name is")[-1].strip()
        context_state["pending_memory"] = {"type": "user_name", "value": name}
        return f"Do you want me to remember that your name is {name}?"

    if "remember that" in command:
        fact = command.split("remember that")[-1].strip()
        context_state["pending_memory"] = {"type": "general_fact", "value": fact}
        return f"Do you want me to permanently save the following information: '{fact}'?"

    # Retrieval Engine
    if "who am i" in command or "my name" in command:
        name = get_memory("user_name")
        return f"Your name is {name}." if name else "I don't believe you have told me your name yet."

    if "what do you remember" in command:
        mem = load_memory()
        facts = mem.get("general_facts", [])
        if not facts: return "I don't have any specific facts memorized at the moment."
        return f"I have several items in my database. The last thing you told me to remember was: {facts[-1]}"

    return None
