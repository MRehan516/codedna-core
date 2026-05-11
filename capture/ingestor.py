import sqlite3
import os
import time
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")
DB_PATH = Path(".codedna/events.db")
FLUSH_INTERVAL = 10  # Flushes every 10 seconds for the demo

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Supabase credentials missing in .env")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def flush():
    if not DB_PATH.exists():
        return
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM events WHERE committed = 0").fetchall()
    if not rows:
        conn.close()
        return
    
    payload = [dict(r) for r in rows]
    for p in payload:
        p.pop("id")  # let Supabase generate its own UUID
    
    try:
        supabase.table("events").insert(payload).execute()
        ids = [r["id"] for r in rows]
        placeholders = ",".join("?" * len(ids))
        conn.execute(f"UPDATE events SET committed=1 WHERE id IN ({placeholders})", ids)
        conn.commit()
        print(f"[Ingestor] ✅ Flushed {len(payload)} events to Supabase.")
    except Exception as e:
        print(f"[Ingestor] ⚠️ Flush failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print(f"[Ingestor] Started. Flushing to Supabase every {FLUSH_INTERVAL} seconds...")
    while True:
        flush()
        time.sleep(FLUSH_INTERVAL)