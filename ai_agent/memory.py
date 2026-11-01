import sqlite3
import os
import json
import time

class AgentMemory:
    """
    Long-term Memory System for the Autonomous AI Agent.
    Stores and retrieves user preferences, frequent apps, common directories,
    favourite browser, preferred language, and recent task context.
    """
    def __init__(self, db_path=None):
        if db_path is None:
            data_dir = os.path.join(os.path.dirname(__file__), "..", "jarvis_data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.abspath(os.path.join(data_dir, "ai_agent_memory.db"))
            
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS preferences (
                        key TEXT PRIMARY KEY,
                        value TEXT,
                        updated_at REAL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS frequent_items (
                        category TEXT,
                        item_name TEXT,
                        count INTEGER DEFAULT 1,
                        last_used REAL,
                        PRIMARY KEY (category, item_name)
                    )
                """)
                conn.commit()
        except Exception as e:
            print(f"[AGENT MEMORY ERROR] DB initialization failed: {e}")

    def set_preference(self, key, value):
        """Save or update a key-value preference."""
        try:
            val_str = json.dumps(value) if not isinstance(value, str) else value
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO preferences (key, value, updated_at) VALUES (?, ?, ?)",
                    (key, val_str, time.time())
                )
                conn.commit()
        except Exception as e:
            print(f"[AGENT MEMORY ERROR] Set preference failed: {e}")

    def get_preference(self, key, default=None):
        """Retrieve a preference by key."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
                row = cursor.fetchone()
                if row:
                    try:
                        return json.loads(row[0])
                    except Exception:
                        return row[0]
        except Exception as e:
            print(f"[AGENT MEMORY ERROR] Get preference failed: {e}")
        return default

    def record_usage(self, category, item_name):
        """Record usage count for apps, websites, folders, or workflows."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO frequent_items (category, item_name, count, last_used)
                    VALUES (?, ?, 1, ?)
                    ON CONFLICT(category, item_name) DO UPDATE SET
                        count = count + 1,
                        last_used = ?
                """, (category, item_name, time.time(), time.time()))
                conn.commit()
        except Exception as e:
            print(f"[AGENT MEMORY ERROR] Record usage failed: {e}")

    def get_top_items(self, category, limit=5):
        """Get top used items in a category."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT item_name, count FROM frequent_items
                    WHERE category = ?
                    ORDER BY count DESC, last_used DESC
                    LIMIT ?
                """, (category, limit))
                return cursor.fetchall()
        except Exception as e:
            print(f"[AGENT MEMORY ERROR] Get top items failed: {e}")
            return []

    def get_all_preferences(self):
        """Return dict of all stored preferences."""
        result = {
            "favourite_browser": self.get_preference("favourite_browser", "chrome"),
            "preferred_language": self.get_preference("preferred_language", "english"),
            "downloads_path": self.get_preference("downloads_path", os.path.expanduser("~/Downloads")),
            "documents_path": self.get_preference("documents_path", os.path.expanduser("~/Documents")),
            "recent_tasks": self.get_preference("recent_tasks", [])
        }
        return result

    def log_recent_task(self, task_goal):
        """Add a task goal to recent tasks list (max 10)."""
        recent = self.get_preference("recent_tasks", [])
        if not isinstance(recent, list):
            recent = []
        if task_goal in recent:
            recent.remove(task_goal)
        recent.insert(0, task_goal)
        recent = recent[:10]
        self.set_preference("recent_tasks", recent)
