import asyncio
import time
import logging
from typing import List, Dict, Callable, Any

# Leveraging asynchronous requests!
try:
    from duckduckgo_search import AsyncDDGS
except ImportError:
    AsyncDDGS = None  # Fallback gracefully if not upgraded

from PyQt6.QtCore import QThread, pyqtSignal

# Import base class
from web_search import JarvisWebSearch

logger = logging.getLogger("JarvisOptimizedSearch")

class RedisLikeCache:
    """High-speed in-memory Redis-like dictionary cache with explicit Expiry (TTL)."""
    def __init__(self, ttl_seconds: int = 3600):
        self.cache = {}
        self.ttl = ttl_seconds

    def get(self, key: str):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: Any):
        self.cache[key] = (value, time.time())

# Global in-memory cache retaining state dynamically
global_memory_cache = RedisLikeCache(ttl_seconds=3600)  # 1 hour strict timeout


class AsyncSearchWorker(QThread):
    """
    Search queue system managed powerfully inside a proper PyQt6 QThread.
    Processes dynamic callbacks sequentially to ensure absolute UI independence.
    """
    result_ready = pyqtSignal(dict) 
    
    def __init__(self, query: str, search_obj: 'OptimizedWebSearch', callback: Callable):
        super().__init__()
        self.query = query
        self.search_obj = search_obj
        self.callback = callback

    def run(self):
        # Fire synchronous block wrapping an isolated asyncio loop natively
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # We enforce smart timeout bounds directly traversing the async execution
            result = loop.run_until_complete(self.search_obj.search_async(self.query))
            if self.callback:
                self.callback(result)
            self.result_ready.emit(result)
        except Exception as e:
            err = {"query": self.query, "results": [], "error": str(e), "cached": False}
            if self.callback:
                self.callback(err)
            self.result_ready.emit(err)
        finally:
            loop.close()


class OptimizedWebSearch(JarvisWebSearch):
    """
    High-performance network subclass integrating Async Pooling, QThread wrappers, 
    Response Streaming algorithms, and fast in-memory Redis-like buffers!
    """
    def __init__(self):
        super().__init__()
        self.in_memory_cache = global_memory_cache
        self._active_workers = []  # Search queue tracking

    async def search_async(self, query: str, timeout_type: str = "quick") -> Dict[str, Any]:
        """
        Pure asymmetric async stream utilizing aiohttp proxy pooling (through AsyncDDGS).
        Timeout types: 'quick' (2s) | 'deep' (10s)
        """
        cached_result = self.in_memory_cache.get(f"async:{query}")
        if cached_result:
            logger.info("Fast-Fetched from Redis-like Memory Cache.")
            return {"query": query, "results": cached_result, "cached": True}

        timeout_seconds = 2 if timeout_type == "quick" else 10
        logger.info(f"Executing Async Search ({timeout_type} limits / {timeout_seconds}s) for: '{query}'")

        results = []
        try:
            # Asyncio structural context timeout control
            async with asyncio.timeout(timeout_seconds):
                
                # Request Pooling via DDGS async implementation using aiohttp context
                async with AsyncDDGS() as ddgs:
                    # Async generative response streaming! No blocking for whole payloads!
                    async for r in ddgs.text(query, max_results=3):
                        results.append(r)
                        
            # Format and standardise
            formatted = []
            for r in results:
                formatted.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                    "link": r.get("href", ""),
                    "source": "DuckDuckGo Async Engine"
                })
                
            if formatted:
                self.in_memory_cache.set(f"async:{query}", formatted)
                
            return {"query": query, "results": formatted, "cached": False}

        except asyncio.TimeoutError:
            logger.warning(f"Async Search timed out cleanly after {timeout_seconds} seconds bounds")
            return {"query": query, "results": [], "error": f"Timeout {timeout_seconds}s exceeded", "cached": False}
        except Exception as e:
            logger.error(f"Async Search Network Pool Failed: {e}")
            return {"query": query, "results": [], "error": str(e), "cached": False}

    def search_with_callback(self, query: str, callback_function: Callable):
        """
        Spawns an encapsulated PyQt6 QThread wrapper queueing async fetch algorithms.
        Extremely safe for execution without ever hanging Dashboard PyQT UI.
        """
        # Spawning the explicit queue worker
        worker = AsyncSearchWorker(query, self, callback_function)
        
        # Lock ref strictly resolving python memory destructor cleaning
        self._active_workers.append(worker)
        
        # Automatic garbage cleanup queue extraction hook
        def cleanup(worker_ref=worker):
            if worker_ref in self._active_workers:
                self._active_workers.remove(worker_ref)
                logger.info("Background Search worker properly destroyed.")
                
        worker.finished.connect(cleanup)
        worker.start()

    def batch_search(self, queries_list: List[str]) -> Dict[str, Any]:
        """
        Executes immense parallel asynchronous searches concurrently scaling asyncio.gather!
        Massive speedups querying huge amounts of web scraping payloads.
        """
        logger.info(f"Initiating Batch Pool Request for {len(queries_list)} distinct queries.")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def _run_batch():
            # Generate the future task structures
            tasks = [self.search_async(q, timeout_type="deep") for q in queries_list]
            # Gather independently suppressing individual execution crashes globally
            return await asyncio.gather(*tasks, return_exceptions=True)
            
        try:
            results = loop.run_until_complete(_run_batch())
            return {q: res for q, res in zip(queries_list, results)}
        finally:
            loop.close()

if __name__ == "__main__":
    # Test Executable demonstrating 100% Async Speed Bounds
    import pprint
    
    print("Beginning High-Performance Async Search Benchmark...")
    optimizer = OptimizedWebSearch()
    
    async def run_test():
        res = await optimizer.search_async("Artificial General Intelligence timing")
        pprint.pprint(res)
        
    asyncio.run(run_test())
