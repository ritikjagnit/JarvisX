import re
import time
import logging
from typing import Dict, Tuple

# Import the core search engine we generated previously!
from web_search import JarvisWebSearch

logger = logging.getLogger("JarvisSearchHandler")

class SearchCache:
    """Simple LRU-style cache to avoid duplicate requests within a 10-minute timeframe."""
    def __init__(self, ttl_seconds: int = 600):
        self.cache: Dict[str, Tuple[str, float]] = {}
        self.ttl = ttl_seconds

    def get(self, query: str) -> str:
        if query in self.cache:
            result, timestamp = self.cache[query]
            if time.time() - timestamp < self.ttl:
                print(f"[CACHE HIT] Loaded instantly for: '{query}'")
                return result
            else:
                del self.cache[query] # Purge stale memory
        return ""

    def set(self, query: str, result: str):
        self.cache[query] = (result, time.time())

# Global cache instance spanning the lifespan of Jarvis runtime
_search_cache = SearchCache()

def handle_search_command(voice_text: str, searcher: JarvisWebSearch) -> str:
    """
    Parses natural language search commands and fetches summarized responses.
    
    Args:
        voice_text (str): The raw voice command/text input.
        searcher (JarvisWebSearch): Instantiated searcher module.
        
    Returns:
        str: Clean TTS-ready response string, or an empty string if query didn't match.
    """
    command = voice_text.lower().strip()
    
    # 1. Parse intent and extract the actual query using Regex Regex
    query = ""
    is_news = False
    
    news_patterns = [
        r"latest news about (.*)",
        r"news about (.*)"
    ]
    
    search_patterns = [
        r"search for (.*)",
        r"find information about (.*)",
        r"tell me about (.*)",
        r"what is (.*)",
        r"who is (.*)",
        r"what are (.*)",
        r"who are (.*)"
    ]

    # Check news intent first
    for pattern in news_patterns:
        match = re.search(pattern, command)
        if match:
            query = match.group(1).strip()
            is_news = True
            break
            
    # Check general search intent
    if not query:
        for pattern in search_patterns:
            match = re.search(pattern, command)
            if match:
                extracted = match.group(1).strip()
                # Reconstruct the question gracefully to provide perfect context for the web fetcher
                if pattern.startswith("what") or pattern.startswith("who"):
                    query = f"{pattern.split(' (')[0]} {extracted}"
                else:
                    query = extracted
                break
                
    if not query:
        # Returning an empty string signifies a non-search-related command
        return ""
        
    query = query.replace("?", "").strip()
    
    # 2. Check Temporary Search Cache!
    cache_key = f"news:{query}" if is_news else f"search:{query}"
    cached_result = _search_cache.get(cache_key)
    if cached_result:
        return cached_result
        
    # 3. Execute Core Search using the Offline DDG logic
    response_text = ""
    try:
        if is_news:
            news_results = searcher.search_news(query, max_results=2)
            if news_results:
                titles = [f"{i+1}. {news['title']}" for i, news in enumerate(news_results)]
                response_text = f"Here is the latest news regarding {query}: " + ", ".join(titles) + "."
            else:
                response_text = f"I couldn't find any recent news about {query}."
        else:
            # Drop straight into the snippet synthesizer logic
            response_text = searcher.answer_question(query)
            
            # Graceful TTS fallback if nothing is returned
            if "I couldn't find" in response_text or not response_text:
                response_text = f"I'm sorry, I couldn't find a direct answer for {query} on the web."
                
    except Exception as e:
        logger.error(f"Search Handler Error: {e}")
        response_text = "I encountered a network error while searching the web."
        
    # 4. Clean up string for TTS (remove brackets, strange HTML formatting marks, etc)
    tts_ready_response = re.sub(r'\[.*?\]', '', response_text) # Excludes citation brackets e.g., [1]
    tts_ready_response = tts_ready_response.replace("...", ".") # Prevents awkward TTS pauses
    
    # 5. Lock in Cache and return TTS string
    _search_cache.set(cache_key, tts_ready_response)
    
    return tts_ready_response

def demo_search_handler():
    """Demo function showcasing usage parsing examples."""
    print("Booting Web Engine...\n")
    searcher = JarvisWebSearch()
    
    test_commands = [
        "search for quantum computing",
        "who is the ceo of google?",
        "what is the distance to the moon?",
        "latest news about artificial intelligence",
        # Adding a duplicate to forcefully trigger the cache logic demonstration
        "who is the ceo of google?"
    ]
    
    print("--- Testing Jarvis Search Handler ---")
    for cmd in test_commands:
        print(f"\\nUser: {cmd}")
        
        # Core Implementation Example!
        response = handle_search_command(cmd, searcher)
        
        if response:
            print(f"Jarvis: {response}")
        else:
            print(f"Jarvis: (No Search Triggered)")

if __name__ == "__main__":
    demo_search_handler()
