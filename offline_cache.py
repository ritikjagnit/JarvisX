import os
import json
import time
import socket
import logging

logger = logging.getLogger("JarvisOfflineCache")
CACHE_FILE = "jarvis_knowledge_base.json"
MAX_CACHE_ITEMS = 1000
SEVEN_DAYS_SECONDS = 7 * 24 * 60 * 60

def check_internet_conn() -> bool:
    """Quickly pings public DNS to evaluate active connectivity."""
    try:
        # Google DNS ping, 2-second timeout
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        pass
    return False

def load_knowledge_base() -> dict:
    """Loads the database and cleans expired items autonomously."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Clean expired items implicitly on load
            current_time = time.time()
            valid_data = {}
            for query, payload in data.items():
                if current_time - payload.get("timestamp", 0) < SEVEN_DAYS_SECONDS:
                    valid_data[query] = payload
                    
            if len(valid_data) != len(data):
                # Save the cleaned dict so the file doesn't constantly bloat
                _save_db(valid_data)
                
            return valid_data
        except Exception as e:
            logger.error(f"Failed to load cache DB: {e}")
            return {}
    return {}

def _save_db(data: dict):
    # Enforce hard limits memory allocation
    if len(data) > MAX_CACHE_ITEMS:
        # Sort by timestamp (index 1 dictionary -> 'timestamp') and keep newest 1000
        sorted_items = sorted(data.items(), key=lambda x: x[1].get("timestamp", 0), reverse=True)
        data = dict(sorted_items[:MAX_CACHE_ITEMS])
        
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save cache DB: {e}")

def search_local(query: str) -> list:
    """Returns raw structured cached result dictionaries."""
    db = load_knowledge_base()
    query = query.lower().strip()
    return db.get(query, {}).get("results", [])

def update_local_cache(query: str, results: list, response: str = ""):
    """Presents queried results and syntheses directly to the offline JSON store."""
    db = load_knowledge_base()
    query = query.lower().strip()
    
    # Do not overwrite a cached response formulation purely with raw results if it exists
    existing_response = db.get(query, {}).get("response", "")
    final_response = response if response else existing_response

    db[query] = {
        "timestamp": time.time(),
        "results": results,
        "response": final_response
    }
    _save_db(db)

def get_cached_response(question: str) -> str:
    """Looks specifically for cleanly synthesized answers (i.e. answer_question format)"""
    db = load_knowledge_base()
    question = question.lower().strip()
    return db.get(question, {}).get("response", "")
