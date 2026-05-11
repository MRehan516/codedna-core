import os
import random
import uuid
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Supabase credentials missing in .env")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
files = ["services/llm.py", "api/routes.ts", "components/Button.tsx", "utils/parser.py", "lib/auth.go"]
events = []
now = datetime.utcnow()

print("Generating 30 days of telemetry data...")
for i in range(30):
    date = now - timedelta(days=30-i)
    # Ramping AI usage narrative for the demo
    num_events = random.randint(5, 15) + (i // 2)
    for _ in range(num_events):
        is_ai = random.random() < (0.2 + (i * 0.02)) 
        events.append({
            "file_path": random.choice(files),
            "block_hash": uuid.uuid4().hex[:16],
            "char_delta": random.randint(50, 500),
            "ai_flagged": is_ai,
            "confirmed": is_ai and random.random() > 0.4,
            "complexity_score": round(random.uniform(1.0, 9.0), 1) if is_ai else round(random.uniform(1.0, 4.0), 1),
            "session_id": "seed-demo",
            "timestamp": date.isoformat()
        })

print(f"Inserting {len(events)} events into Supabase...")
for i in range(0, len(events), 100):
    supabase.table("events").insert(events[i:i+100]).execute()

print("✅ Seed complete! CodeDNA is ready for the demo.")