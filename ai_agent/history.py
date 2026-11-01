import sqlite3
import os
import time
from datetime import datetime

class ExecutionHistory:
    """
    Execution History Logger for Autonomous AI Agent.
    Records task runs into SQLite database:
    Fields: id, timestamp, task_goal, status, duration_seconds, errors, result_summary
    """
    def __init__(self, db_path=None):
        if db_path is None:
            data_dir = os.path.join(os.path.dirname(__file__), "..", "jarvis_data")
            os.makedirs(data_dir, exist_ok=True)
            db_path = os.path.abspath(os.path.join(data_dir, "ai_agent_history.db"))
            
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        task_goal TEXT,
                        status TEXT,
                        duration_seconds REAL,
                        errors TEXT,
                        result_summary TEXT
                    )
                """)
                conn.commit()
        except Exception as e:
            print(f"[EXECUTION HISTORY ERROR] DB initialization failed: {e}")

    def log_execution(self, task_goal, status, duration_seconds, errors="", result_summary=""):
        """Record a completed or failed task execution."""
        try:
            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO history (timestamp, task_goal, status, duration_seconds, errors, result_summary)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (timestamp_str, task_goal, status, round(duration_seconds, 2), str(errors), str(result_summary)))
                conn.commit()
                print(f"[HISTORY LOGGED] Task: '{task_goal}' | Status: {status} | Duration: {round(duration_seconds, 2)}s")
        except Exception as e:
            print(f"[EXECUTION HISTORY ERROR] Log failed: {e}")

    def get_recent_history(self, limit=20):
        """Fetch recent execution history records as dicts."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, timestamp, task_goal, status, duration_seconds, errors, result_summary
                    FROM history
                    ORDER BY id DESC
                    LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            print(f"[EXECUTION HISTORY ERROR] Fetch history failed: {e}")
            return []

    def get_stats(self):
        """Get summary statistics of task executions."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*), SUM(CASE WHEN status='SUCCESS' THEN 1 ELSE 0 END) FROM history")
                total, success = cursor.fetchone()
                total = total or 0
                success = success or 0
                return {
                    "total_tasks": total,
                    "success_tasks": success,
                    "failed_tasks": total - success,
                    "success_rate": round((success / total * 100), 1) if total > 0 else 100.0
                }
        except Exception as e:
            print(f"[EXECUTION HISTORY ERROR] Get stats failed: {e}")
            return {"total_tasks": 0, "success_tasks": 0, "failed_tasks": 0, "success_rate": 100.0}
