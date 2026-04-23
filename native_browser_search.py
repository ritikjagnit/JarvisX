import re
import urllib.parse
import webbrowser
import logging

# Basic logger for debugging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("NativeBrowserSearch")

def _safe_math_eval(expr: str):
    """
    Securely evaluates basic mathematical expressions using Python's standard 
    capabilities without opening dangerous vector holes with unrestricted eval().
    """
    try:
        # Strip all alphabetical characters, keeping only numbers and operators
        safe_expr = re.sub(r'[^0-9+\-*/. ()]', '', expr)
        if not safe_expr.strip():
            return None
            
        # Passing an entirely empty scope blocks code execution exploits
        result = eval(safe_expr, {"__builtins__": None}, {})
        
        # Format cleanly for speech synthesis
        return round(result, 3) if isinstance(result, float) else result
    except Exception as e:
        logger.error(f"Math calculation failed for '{expr}': {e}")
        return None

def handle_search_command(command_text: str) -> str:
    """
    Parses voice intents seamlessly launching searches in the default system browser!
    Fully decoupled from 3rd party packages like PIP. Uses Only Python Standard Library.
    
    Args:
        command_text (str): Voice transcribed intent string.
        
    Returns:
        str: Clean TTS response to speak aloud.
    """
    
    cmd = command_text.lower().strip()
    if not cmd:
        return "I did not recognize the search parameters."
        
    try:
        # 1. TRANSLATION (translate [text] to [language])
        translate_match = re.search(r"translate (.*) to (.*)", cmd)
        if translate_match:
            text = translate_match.group(1).strip()
            # Map basic language names to google prefixes (or rely on auto-identification tools)
            lang = translate_match.group(2).strip()
            
            # Map full language name to a safe string for URL
            encoded_text = urllib.parse.quote(text)
            encoded_lang = urllib.parse.quote(lang)
            
            url = f"https://translate.google.com/?sl=auto&tl={encoded_lang}&text={encoded_text}&op=translate"
            webbrowser.open(url)
            return f"Opening translation for {text} into {lang}."

        # 2. DEFINITIONS / QUESTIONS (what is [topic])
        question_match = re.search(r"what is (.*)|who is (.*)", cmd)
        if question_match:
            # Reconstruct the question
            topic = "what is " + next((m for m in question_match.groups() if m), cmd).strip()
            encoded_query = urllib.parse.quote(topic)
            url = f"https://duckduckgo.com/?q={encoded_query}"
            webbrowser.open(url)
            return "Searching the web for the answer right now, sir."

        # 3. WIKIPEDIA ENTRY (wiki [topic])
        wiki_match = re.search(r"wiki (.*)", cmd)
        if wiki_match:
            topic = wiki_match.group(1).strip()
            # Wikipedia URLs generally separate words via underscores natively
            formatted_topic = "_".join([word.capitalize() for word in topic.split()])
            encoded_query = urllib.parse.quote(formatted_topic)
            url = f"https://en.wikipedia.org/wiki/{encoded_query}"
            webbrowser.open(url)
            return f"Pulling up the Wikipedia encyclopedia page for {topic}."

        # 4. MATHEMATICS (calculate [expr])
        calc_match = re.search(r"calculate (.*)|what is (\d+.*)", cmd)
        if calc_match:
            expr = next((m for m in calc_match.groups() if m), cmd).strip()
            result = _safe_math_eval(expr)
            if result is not None:
                return f"The calculated result is {result}."
            else:
                # Fallback to web search if the math engine breaks Down
                encoded_query = urllib.parse.quote(cmd)
                webbrowser.open(f"https://duckduckgo.com/?q={encoded_query}")
                return "Calculating math using web assistance."

        # 5. NEWS SEARCH (news about [topic])
        news_match = re.search(r"news about (.*)|latest news (.*)", cmd)
        if news_match:
            topic = next((m for m in news_match.groups() if m), "global").strip()
            encoded_query = urllib.parse.quote(topic)
            url = f"https://news.google.com/search?q={encoded_query}"
            webbrowser.open(url)
            return f"Opening the latest news headlines regarding {topic}."

        # 6. GENERAL SEARCH ENGINE ("search for [topic]")
        search_match = re.search(r"search for (.*)|find (.*)", cmd)
        if search_match:
            topic = next((m for m in search_match.groups() if m), cmd).strip()
            encoded_query = urllib.parse.quote(topic)
            url = f"https://duckduckgo.com/?q={encoded_query}"
            webbrowser.open(url)
            return f"Executing web search for {topic}."

        return "" # Returns empty if totally unhandled
        
    except Exception as e:
        logger.error(f"Routing module failed to execute browser fetch: {e}")
        return "I encountered a system error generating your web link."

if __name__ == '__main__':
    # Unit Execution Testing Protocol
    print("Testing Native Browser Routing without External Packages...")
    commands = [
        "search for python standard libraries",
        "wiki albert einstein",
        "calculate 550 * 3", 
        "translate hello my friend to spanish",
        "news about space station",
        "what is quantum physics"
    ]
    
    for cmd in commands:
        response = handle_search_command(cmd)
        print(f"Command: '{cmd}' -> Jarvis Speaks: '{response}'")
