import sqlite3
from pathlib import Path

DB_PATH = Path(".codedna/events.db")

def get_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=5)
    # Enable Write-Ahead Logging for concurrent access
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            block_hash TEXT NOT NULL,
            line_start INTEGER,
            line_end INTEGER,
            char_delta INTEGER,
            ai_flagged INTEGER DEFAULT 0,
            confirmed INTEGER DEFAULT 0,
            complexity_score REAL DEFAULT 0.0,
            session_id TEXT,
            timestamp TEXT DEFAULT (datetime('now')),
            committed INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    return conn

def insert_event(file_path, block_hash, line_start, line_end, char_delta, ai_flagged, complexity_score, session_id):
    db = get_db()
    db.execute("""
        INSERT INTO events 
        (file_path, block_hash, line_start, line_end, char_delta, ai_flagged, complexity_score, session_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (str(file_path), block_hash, line_start, line_end, char_delta, int(ai_flagged), complexity_score, session_id))
    db.commit()
    db.close()