import sqlite3
import os
import json
import time
import datetime

DB_PATH = os.path.join("jarvis_data", "remote_nexus.db")

def get_db():
    if not os.path.exists("jarvis_data"):
        os.makedirs("jarvis_data")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_remote_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. Paired Devices Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paired_devices (
            device_id TEXT PRIMARY KEY,
            device_name TEXT NOT NULL,
            device_type TEXT NOT NULL,
            ip_address TEXT,
            public_key TEXT,
            secret_key TEXT,
            status TEXT DEFAULT 'ACTIVE',
            created_at REAL,
            last_active REAL
        )
    """)

    # 2. Audit Logs Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            device_id TEXT,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            ip_address TEXT,
            details TEXT
        )
    """)

    # 3. Scheduled Automations Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS automations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            command TEXT NOT NULL,
            trigger_type TEXT NOT NULL,
            trigger_value TEXT,
            is_active INTEGER DEFAULT 1,
            created_at REAL
        )
    """)

    # 4. Conversation Remote History Cache
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS remote_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            device_id TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("[REMOTE DB] Database initialized successfully at:", DB_PATH)

def register_device(device_id: str, device_name: str, device_type: str, ip_address: str = "", secret_key: str = "") -> dict:
    conn = get_db()
    cursor = conn.cursor()
    now = time.time()
    
    cursor.execute("""
        INSERT OR REPLACE INTO paired_devices (device_id, device_name, device_type, ip_address, secret_key, status, created_at, last_active)
        VALUES (?, ?, ?, ?, ?, 'ACTIVE', ?, ?)
    """, (device_id, device_name, device_type, ip_address, secret_key, now, now))
    
    conn.commit()
    conn.close()
    return {"device_id": device_id, "device_name": device_name, "status": "ACTIVE"}

def get_paired_devices() -> list:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM paired_devices WHERE status = 'ACTIVE' ORDER BY last_active DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def revoke_device(device_id: str) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE paired_devices SET status = 'REVOKED' WHERE device_id = ?", (device_id,))
    conn.commit()
    count = cursor.rowcount
    conn.close()
    return count > 0

def update_device_active(device_id: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE paired_devices SET last_active = ? WHERE device_id = ?", (time.time(), device_id))
    conn.commit()
    conn.close()

def log_audit_event(action: str, status: str = "SUCCESS", device_id: str = "SYSTEM", ip_address: str = "127.0.0.1", details: str = ""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (timestamp, device_id, action, status, ip_address, details)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (time.time(), device_id, action, status, ip_address, details))
    conn.commit()
    conn.close()

def get_recent_audit_logs(limit: int = 50) -> list:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_chat_history(sender: str, message: str, device_id: str = "LOCAL"):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO remote_history (timestamp, sender, message, device_id)
        VALUES (?, ?, ?, ?)
    """, (time.time(), sender, message, device_id))
    conn.commit()
    conn.close()

def get_chat_history(limit: int = 40) -> list:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM remote_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    res = [dict(r) for r in rows]
    res.reverse()
    return res

# Initialize DB on module load
init_remote_db()
