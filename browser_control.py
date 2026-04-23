import webbrowser
from urllib.parse import quote_plus

def process_browser_command(command, context_state=None):
    if command.startswith("open youtube"):
        webbrowser.open("https://youtube.com")
        if context_state is not None:
             context_state['last_platform'] = 'youtube'
        return "Opening YouTube"

    if command.startswith("search youtube "):
        query = command.replace("search youtube ", "").strip()
        if not query: return "What do you want to search on YouTube?"
        webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
        if context_state is not None:
            context_state['last_platform'] = 'youtube'
        return f"Searching YouTube for {query}."

    if command.startswith("search google ") or command.startswith("search for "):
        query = command.replace("search google ", "").replace("search for ", "").strip()
        if not query: return "What do you want to search?"
        webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
        if context_state is not None:
            context_state['last_platform'] = 'google'
        return f"Searching Google for {query}."

    if command.startswith("open google"):
        query = command.replace("open google", "").strip()
        if query:
            webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
            if context_state is not None:
                context_state['last_platform'] = 'google'
            return f"Searching Google for {query}."
        else:
            webbrowser.open("https://google.com")
            if context_state is not None:
                context_state['last_platform'] = 'google'
            return "Opening Google."

    if command.startswith("open instagram"):
        webbrowser.open("https://instagram.com")
        return "Opening Instagram"
        
    if command.startswith("open whatsapp"):
        webbrowser.open("https://web.whatsapp.com")
        return "Opening WhatsApp Web"
        
    # CONTEXT UNDERSTANDING
    # If user says "search cats", and last platform was youtube, search youtube directly.
    if command.startswith("search ") and context_state is not None:
        last = context_state.get('last_platform')
        query = command.replace("search", "").strip()
        if last == 'youtube':
            webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
            return f"Since you were using YouTube, I am searching YouTube for {query}."
        elif last == 'google':
            webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
            return f"Since you were using Google, I am searching Google for {query}."

    return None
