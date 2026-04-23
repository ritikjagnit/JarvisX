import time
import requests
import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from offline_cache import check_internet_conn, search_local, update_local_cache, get_cached_response

try:
    import wikipediaapi
    wiki_wiki = wikipediaapi.Wikipedia(
        user_agent='JarvisWebSearchEngine/1.0 (jarvis@assistant.com)',
        language='en'
    )
except ImportError:
    wiki_wiki = None

try:
    import wolframalpha
    # Replace with real App ID to activate Wolfram calculations
    WOLFRAM_APP_ID = os.environ.get("WOLFRAM_APP_ID", "")
    wolfram_client = wolframalpha.Client(WOLFRAM_APP_ID) if WOLFRAM_APP_ID else None
except ImportError:
    wolfram_client = None

# Setup basic logging for the web search module
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("JarvisWebSearch")

class JarvisWebSearch:
    """
    A production-ready module to handle realtime web search strictly for Jarvis AI.
    Features built-in rate limiting, error handling, and offline fail-safes without requiring
    paid external APIs.
    """
    
    def __init__(self):
        self.last_request_time = 0.0
        self.rate_limit_delay = 0.5  # Seconds to wait between subsequent network polling

    def _rate_limit(self):
        """Enforces a 0.5s delay between active network calls to prevent IP blocking."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    def search_web(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Searches the web using DuckDuckGo.
        
        Args:
            query (str): The search phrase.
            max_results (int): Maximum number of results to fetch.
            
        Returns:
            List[Dict[str, str]]: A list of dictionaries containing title, link, snippet, and source.
        """
        self._rate_limit()
        logger.info(f"Performing web search for: '{query}'")
        
        # OFFLINE OVERRIDE: Check local database first!
        cached_results = search_local(query)
        if cached_results:
            logger.info(f"[{query}] Located in absolute offline cache. Rendering directly.")
            return cached_results
            
        # NETWORK CHECK: Determine if we have power to reach global internet
        if not check_internet_conn():
            logger.warning("Internet disconnected. No local cache exists. Running blind.")
            return []

        results = []
        try:
            with DDGS() as ddgs:
                ddg_results = ddgs.text(query, max_results=max_results)
                for res in ddg_results:
                    results.append({
                        "title": res.get("title", "No Title Found"),
                        "link": res.get("href", ""),
                        "snippet": res.get("body", "No Snippet Available"),
                        "source": "DuckDuckGo"
                    })
                    
            if results:
                # Update our persistent database to build offline resilience
                update_local_cache(query, results)
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            results = self._fallback_search(query, max_results)
            
        return results

    def search_news(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Fetches the latest news articles for a given topic.
        
        Args:
            query (str): The news topic.
            max_results (int): Maximum news articles to fetch.
            
        Returns:
            List[Dict[str, str]]: A list of news articles with date and source.
        """
        self._rate_limit()
        logger.info(f"Performing news search for: '{query}'")
        
        # Check offline cache
        cached_results = search_local(f"news: {query}")
        if cached_results:
            logger.info("Serving recent news from offline local storage.")
            return cached_results
            
        if not check_internet_conn():
            logger.warning("Network failure. News cannot be fetched dynamically.")
            return []

        results = []
        try:
            with DDGS() as ddgs:
                ddg_news = ddgs.news(query, max_results=max_results)
                for res in ddg_news:
                    results.append({
                        "title": res.get("title", "No Title"),
                        "link": res.get("url", ""),
                        "snippet": res.get("body", "No Snippet"),
                        "date": res.get("date", "Unknown Date"),
                        "source": res.get("source", "DuckDuckGo News")
                    })
            if results:
                update_local_cache(f"news: {query}", results)
        except Exception as e:
            logger.error(f"DuckDuckGo news failed: {e}")
        
        return results

    def fetch_page_content(self, url: str) -> Optional[str]:
        """
        Extracts clean text content from a webpage URL natively bypassing JavaScript.
        
        Args:
            url (str): Target webpage URL.
            
        Returns:
            Optional[str]: Extracted text, or None if network failure occurs.
        """
        self._rate_limit()
        logger.info(f"Fetching page content from: {url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=8)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts, styles, and junk metadata structures
            for script in soup(["script", "style", "header", "footer", "nav"]):
                script.extract()
                
            text = soup.get_text(separator=' ', strip=True)
            # Basic cleanup of extra whitespace block buffers
            clean_text = ' '.join(text.split())
            
            return clean_text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch content from {url}: {e}")
            return None

    def answer_question(self, question: str) -> str:
        """
        Synthesizes an answer using the search snippets without demanding heavy AI API overhead.
        
        Args:
            question (str): The logical inquiry.
            
        Returns:
            str: The synthesized answer snippet read directly to Jarvis.
        """
        logger.info(f"Attempting to answer question: '{question}'")
        
        cached_response = get_cached_response(question)
        if cached_response:
            logger.info("Synthesized answer retrieved naturally from offline memory.")
            return cached_response
        
        # Grab the top 3 highest priority snippets defining the term 
        results = self.search_web(question, max_results=3)
        
        if not results:
            return "I couldn't find any information locally or on the web regarding that."
            
        snippets = [res["snippet"] for res in results if res["snippet"]]
        
        if snippets:
            # Combine snippets cleanly as one cohesive stream
            answer = " ".join(snippets[:2])
            final_resp = f"According to web results: {answer}"
            # Hard-lock synthesis into JSON for sub-millisecond offline fetches
            update_local_cache(question, results, response=final_resp)
            return final_resp
            
        return "I found web results for your inquiry, but I couldn't extract a clear and concise answer."

    def _fallback_search(self, query: str, max_results: int) -> List[Dict[str, str]]:
        """
        Wikipedia native fallback method if DuckDuckGo blocks the IP.
        
        Args:
            query (str): The search phrase.
            max_results (int): Limit returns.
            
        Returns:
            List[Dict[str, str]]: Fallback search dictionary.
        """
        logger.warning("Initiating Wikipedia API Fallback Search...")
        try:
            url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={query}&utf8=&format=json"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("query", {}).get("search", [])[:max_results]:
                # Scrub HTML highlight markers from snippet (like <span class=\\"searchmatch\\">)
                snippet_clean = BeautifulSoup(item.get("snippet", ""), "html.parser").get_text()
                
                results.append({
                    "title": item.get("title", ""),
                    "link": f"https://en.wikipedia.org/wiki/{item.get('title', '').replace(' ', '_')}",
                    "snippet": snippet_clean,
                    "source": "Wikipedia"
                })
            return results
        except Exception as e:
            logger.error(f"Fallback search completely failed: {e}")
            return []

    def search_videos(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        """Searches for YouTube videos via DuckDuckGo metadata."""
        self._rate_limit()
        logger.info(f"Performing video search for: '{query}'")
        cached = search_local(f"video: {query}")
        if cached: return cached
        if not check_internet_conn(): return []
        
        results = []
        try:
            with DDGS() as ddgs:
                for res in ddgs.videos(query, max_results=max_results):
                    if "youtube.com" in res.get("content", "") or "youtu.be" in res.get("content", ""):
                        results.append({
                            "title": res.get("title", "Unknown Title"),
                            "link": res.get("content", ""), 
                            "snippet": res.get("description", ""),
                            "source": "YouTube (DDG)"
                        })
            if results: update_local_cache(f"video: {query}", results)
        except Exception as e:
            logger.error(f"Video search failed: {e}")
        return results

    def search_wikipedia(self, query: str) -> List[Dict[str, str]]:
        """Fetches detailed encyclopedia definitions natively."""
        self._rate_limit()
        logger.info(f"Performing Wikipedia search for: '{query}'")
        cached = search_local(f"wiki: {query}")
        if cached: return cached
        if not check_internet_conn(): return []
        
        results = []
        if wiki_wiki:
            try:
                page = wiki_wiki.page(query)
                if page.exists():
                    results.append({
                        "title": page.title,
                        "link": page.fullurl,
                        "snippet": page.summary[0:500] + "...", 
                        "source": "Wikipedia"
                    })
                if results: update_local_cache(f"wiki: {query}", results)
            except Exception as e:
                logger.error(f"Wikipedia API failed: {e}")
        return results

    def search_wolfram(self, query: str) -> List[Dict[str, str]]:
        """Calculates complex algorithms securely via Wolfram if key is present."""
        self._rate_limit()
        logger.info(f"Performing Wolfram calculation for: '{query}'")
        cached = search_local(f"calc: {query}")
        if cached: return cached
        if not check_internet_conn(): return []
        
        results = []
        if wolfram_client:
            try:
                res = wolfram_client.query(query)
                if res.success:
                    answer = next(res.results).text
                    if answer:
                        results.append({
                            "title": "Mathematical Calculation",
                            "link": "https://www.wolframalpha.com/",
                            "snippet": answer,
                            "source": "Wolfram Alpha"
                        })
                if results: update_local_cache(f"calc: {query}", results)
            except Exception as e:
                logger.error(f"Wolfram query returned no direct answer: {e}")
        return results

    def search_all_sources(self, query: str) -> Dict[str, list]:
        """Runs parallel synchronous database targets across all major APIs."""
        return {
            "duckduckgo": self.search_web(query, max_results=3),
            "wikipedia": self.search_wikipedia(query),
            "news": self.search_news(query, max_results=2),
            "videos": self.search_videos(query, max_results=2),
            "wolfram": self.search_wolfram(query)
        }

    def smart_search(self, query: str) -> str:
        """
        Auto-detects the intent and dispatches to the most accurate database natively.
        Returns the clean response string suitable for TTS.
        """
        import re
        q = query.lower()
        
        # 1. Math & Calculations (Requires WOLFRAM_APP_ID environment variable set)
        if re.search(r"calculate|math|what is \d|times|plus|minus|divided by|square root", q):
            calc = self.search_wolfram(query)
            if calc:
                return f"According to Wolfram Alpha, the calculation result is: {calc[0]['snippet']}"
            else:
                return self.answer_question(query)

        # 2. Definitions / "What is X", "Who is X"
        elif re.match(r"(what is|who is|define) (.*)", q):
            match = re.match(r"(what is|who is|define) (.*)", q)
            subject = match.group(2).strip().replace("?", "")
            
            wiki_res = self.search_wikipedia(subject)
            if wiki_res:
                summary = wiki_res[0]['snippet'].split('.')[0] + "." # Return just the first primary sentence
                return f"According to Wikipedia: {summary}"
            else:
                return self.answer_question(query)
                
        # 3. News
        elif "news" in q or "latest on" in q:
            subject = q.replace("latest news about", "").replace("news about", "").replace("news on", "").strip()
            results = self.search_news(subject, max_results=2)
            if results:
                items = [f"{r['title']}" for r in results]
                return f"Here is the latest news regarding {subject}: " + ", ".join(items)
            return f"I couldn't find any recent news on {subject}."

        # 4. Videos
        elif "video" in q or "youtube" in q:
            subject = q.replace("search youtube for", "").replace("find a video of", "").strip()
            results = self.search_videos(subject, max_results=2)
            if results:
                items = [f"{r['title']}" for r in results]
                return f"I found these primary videos on YouTube: " + ", ".join(items)
            return "I couldn't locate any requested videos on YouTube."
            
        # 5. Default General QA
        else:
            return self.answer_question(query)

    def format_multi_source_response(self, results: Dict[str, list]) -> str:
        """Creates a unified summary dump parsing aggregated JSON lists."""
        response = "Multi-Source Extraction Complete:\n"
        
        if results.get('wikipedia'):
            response += f"📘 WIKIPEDIA: {results['wikipedia'][0]['snippet']}\n"
        if results.get('duckduckgo'):
            response += f"🦆 WEB SEARCH: {results['duckduckgo'][0]['title']} - {results['duckduckgo'][0]['snippet']}\n"
        if results.get('news'):
            response += f"📰 NEWS: {results['news'][0]['title']}\n"
        if results.get('wolfram'):
            response += f"🧮 CALCULATION: {results['wolfram'][0]['snippet']}\n"
            
        return response

if __name__ == "__main__":
    searcher = JarvisWebSearch()
    print("Testing Smart Source Locator:")
    print(searcher.smart_search("define artificial intelligence"))
