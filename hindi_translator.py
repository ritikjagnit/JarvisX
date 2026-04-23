HINDI_TO_ENGLISH = {
    "kholo": "open",
    "band karo": "close",
    "mera naam": "my name is",
    "kya hai": "what is",
    "likho": "write",
    "batao": "tell",
    "khojo": "search",
    "chalao": "play",
    "gaana": "song",
    "samay": "time"
}

def translate_hindi_to_english(command):
    original = command
    command = command.lower()
    for hindi_word, english_word in HINDI_TO_ENGLISH.items():
        if hindi_word in command:
            command = command.replace(hindi_word, english_word)
    
    if command != original:
        print(f"[DEBUG-HINDI] Translated: '{original}' -> '{command}'")
        
    return command.strip()
