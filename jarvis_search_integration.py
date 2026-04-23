import threading
import logging
import time
import re
from typing import Optional, Any

# Assuming standard architectural locations of Jarvis modules
try:
    from web_search import JarvisWebSearch
    from voice_engine import speak, listen
except ImportError as e:
    logging.error(f"[INTEGRATION] Dependency load failure. Are modules present? {e}")

# Detailed module logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger("JarvisSearchIntegration")

class JarvisSearchIntegration:
    """
    Plug-and-play module that masterfully unifies Voice Recognition, Web Fetching, 
    and Terminal Text updating via unblocking background logic threads.
    """
    
    def __init__(self, terminal_instance: Any = None):
        """
        Initialize the master Search Orchestrator.
        
        Args:
            terminal_instance (Any): Your Dashboard's PremiumTerminal (or any class with .append_message)
        """
        self.terminal = terminal_instance
        self.search_engine = JarvisWebSearch() # Native DuckDuckGo with Cache abilities
        self.is_busy = False
        logger.info("Universal Search Integration module loaded securely.")

    def _ui_log(self, sender: str, message: str):
        """Helper to pipe to the visual terminal cleanly if bound."""
        if self.terminal and hasattr(self.terminal, "append_message"):
            try:
                self.terminal.append_message(sender, message)
            except Exception as e:
                logger.error(f"UI Terminal rendering explicitly failed: {e}")
        else:
            # Graceful fallback to pure console if no Terminal UI is attached
            print(f"[{sender}] {message}")
            
    def _safe_speak(self, text: str):
        """Safely pipes text directly to out-of-process voice engine."""
        if text:
            try:
                # Strip out nasty citation blocks like [1], [2] which confuse the TTS reader
                speech_text = re.sub(r'\[.*?\]', '', text)
                speak(speech_text)
            except Exception as e:
                logger.error(f"Text-to-Speech routing failed: {e}")

    def execute_search_async(self, query: str, context: str = "general"):
        """
        Crucial non-blocking wrapper. Spins asynchronous data harvesting routines 
        bypassing PyQt locks completely.
        
        Args:
            query (str): The search input query.
            context (str): Either 'news' or 'general' synthesis.
        """
        if self.is_busy:
            self._ui_log("SYSTEM", "Network search processor is currently occupied.")
            self._safe_speak("Please hold, I am already processing a global query.")
            return

        self.is_busy = True
        
        def _background_fetch_task():
            try:
                # Provide instant visual feedback that command was accepted
                self._ui_log("JARVIS", f"Initiating {context} uplink for '{query}'...")
                
                start_time = time.time()
                response_str = ""
                
                if context == "news":
                    results = self.search_engine.search_news(query, max_results=3)
                    if results:
                        items = [f"{i+1} - {news['title']}" for i, news in enumerate(results)]
                        response_str = f"Here is the latest news regarding {query}: " + ". ".join(items)
                        
                        self._ui_log("JARVIS-WEB", f"News Located: {len(results)} core articles.")
                        for news in results:
                            self._ui_log("NEWS-UPLINK", f"[{news['date']}] {news['title']} - Source: {news['source']}")
                    else:
                        response_str = f"I could not locate any recent news on '{query}'."
                        self._ui_log("JARVIS-WEB", "No metrics found.")
                else:
                    # Leverage the powerful built-in QA synthesis generator directly
                    response_str = self.search_engine.answer_question(query)
                    self._ui_log("JARVIS-WEB", f"Global Synthesis Result: {response_str}")

                # Instruct Jarvis to literally verbalize the web fetch
                self._safe_speak(response_str)
                
                logger.info(f"Query resolution finalized in {round(time.time() - start_time, 2)}s.")
                
            except Exception as e:
                logger.error(f"Search Execution Thread experienced Critical Crash: {e}", exc_info=True)
                self._ui_log("ERROR", "Uplink server error encountered. Query dropped.")
                self._safe_speak("I encountered an error querying the global database.")
            finally:
                self.is_busy = False

        # Spawn detached parallel network execution thread (daemon ensures it closes natively)
        loader_thread = threading.Thread(target=_background_fetch_task, daemon=True, name=f"JarvisAsyncFetch-{time.time()}")
        loader_thread.start()

    def handle_voice_query(self, voice_text: str) -> bool:
        """
        Deep regex interception method matching generalized incoming voice inputs mapped
        into proper robust semantic fetches.
        
        Returns:
            bool: True if intent was recognized and routed, False if it was unrelated.
        """
        command = voice_text.lower().strip()
        if not command:
            return False
            
        # Prioritize checking 'News' intents
        news_matches = re.search(r"latest news about (.*)|news on (.*)|news about (.*)", command)
        if news_matches:
            # Grabs whichever group successfully caught the item target string
            target = next((m for m in news_matches.groups() if m), None)
            if target:
                self._ui_log("USER", voice_text)
                self.execute_search_async(target.strip(), context="news")
                return True

        # Checking common 'Fact / General Search' intents
        search_matches = re.search(r"search for (.*)|tell me about (.*)|who is (.*)|what is (.*)|find information about (.*)", command)
        if search_matches:
            # Prevent context destruction. "Who is the CEO of Google?" fetches better results than "the CEO of Google?"
            if command.startswith("who is") or command.startswith("what is") or command.startswith("what are") or command.startswith("who are"):
                target = command
            else:
                target = next((m for m in search_matches.groups() if m), command)
                
            self._ui_log("USER", voice_text)
            self.execute_search_async(target.strip(), context="general")
            return True
            
        return False

# =========================================================================================
# MAIN PLUG-AND-PLAY INTEGRATION HOOK (USE THIS IN YOUR main.py!)
# =========================================================================================
class NativeMainIntegration:
    """Example snippet structure showcasing exact deployment inside the active GUI loop."""
    
    def __init__(self, premium_terminal):
        # 1. Initialize instance targeting the existing QTextEdit GUI element
        self.search_handler = JarvisSearchIntegration(terminal_instance=premium_terminal)

    def continuous_voice_loop_example(self):
        """Showcasing voice ingestion flow."""
        self.search_handler._ui_log("SYSTEM", "Acoustic web search parser online.")
        
        while True:
            # 2. Grab standard user audio via your engine
            print("Listening for web questions...")
            voice_data = listen() 
            
            if voice_data:
                # 3. If handled, the module skips generic AI processes automatically
                was_handled = self.search_handler.handle_voice_query(voice_data)
                
                if not was_handled:
                    # Proceed to your local command engine or ChatGPT functions safely
                    pass 

if __name__ == '__main__':
    # Raw Unit Tests preventing UI load crashes
    print("Beginning Offline Dependency Test...")
    integration = JarvisSearchIntegration()
    integration.handle_voice_query("who is the ceo of microsoft")
    time.sleep(3) # Wait for parallel process to exit naturally
