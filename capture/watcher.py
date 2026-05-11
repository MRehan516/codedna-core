import time
import hashlib
import os
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv
from . import db
from .detector import detect_ai_insertion

load_dotenv()

WATCH_DIR = os.getenv("CODEDNA_WATCH_DIR", ".")
SUPPORTED_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs"}

class CodeDNAHandler(FileSystemEventHandler):
    def __init__(self, session_id):
        self.session_id = session_id
        self.file_snapshot = {}
        self.last_event_time = {}

    def on_modified(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        # Ignore our own database and unsupported files
        if path.suffix not in SUPPORTED_EXTENSIONS or ".codedna" in path.parts:
            return

        now = time.time()
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return

        prev_size, prev_content = self.file_snapshot.get(str(path), (len(content), content))
        time_delta_ms = (now - self.last_event_time.get(str(path), now - 1)) * 1000

        self.file_snapshot[str(path)] = (len(content), content)
        self.last_event_time[str(path)] = now

        delta = len(content) - prev_size
        if delta <= 0:
            return

        inserted_block = content[-delta:] if delta < len(content) else content
        is_ai_candidate, score, actual_delta = detect_ai_insertion(prev_content, content, time_delta_ms, inserted_block)
        
        if actual_delta <= 0:
            return

        block_hash = hashlib.sha256(f"{inserted_block}{self.session_id}".encode()).hexdigest()[:16]

        # Complexity via radon (Python only)
        complexity = 1.0
        if path.suffix == ".py":
            try:
                from radon.complexity import cc_visit
                results = cc_visit(content)
                if results:
                    complexity = sum(r.complexity for r in results) / len(results)
            except Exception:
                pass

        lines = content.split("\n")
        line_end = len(lines)
        line_start = max(1, line_end - inserted_block.count("\n") - 1)

        db.insert_event(str(path), block_hash, line_start, line_end, actual_delta, is_ai_candidate, complexity, self.session_id)

        flag = "🤖 AI?" if is_ai_candidate else "✍️  Human"
        print(f"[CodeDNA] {flag} | {path.name} | +{actual_delta}c | hash:{block_hash[:8]} | ω:{complexity:.1f}")

def start_watcher():
    import uuid
    session_id = str(uuid.uuid4())[:8]
    db.get_db() # Init schema
    handler = CodeDNAHandler(session_id)
    observer = Observer()
    observer.schedule(handler, WATCH_DIR, recursive=True)
    observer.start()
    print(f"[CodeDNA] Watcher active. Monitoring: {WATCH_DIR} | Session: {session_id}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_watcher()
    