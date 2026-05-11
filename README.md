# **CodeDNA Core Engine**

### CodeDNA is the first Deterministic Capture-at-Generation platform. It cryptographically tags AI-generated code blocks at the exact moment of insertion, tracking their complexity-weighted churn across commits to surface hidden "Shadow AI Debt."

This repository contains the Core Python Capture Engine.
View the Next.js Frontend Dashboard Repository Here: [https://github.com/MRehan516/codedna-frontend](https://github.com/MRehan516/codedna-frontend)

### Architecture: The 3-Layer System
CodeDNA operates locally on the developer's machine with zero IDE extensions required, utilizing a behavioral heuristic pipeline:

1. Capture Layer (watcher.py): Uses watchdog to monitor the file system. It extracts diffs on file modification and evaluates velocity, clipboard cross-referencing, and structural density to flag AI-generated insertions.
2. Buffer Layer (db.py): Hashes the detected block (SHA-256), calculates its cyclomatic complexity using AST parsing (radon), and writes the event to a local, offline-first SQLite database (.codedna/events.db).
3. Sync Layer (ingestor.py): A background worker that flushes pending events to a Supabase PostgreSQL instance for real-time WebSocket broadcasting to the frontend dashboard.

# Quick Start (Local Setup)

## Prerequisites:

* Python 3.10+
* A Supabase project (for telemetry storage)

## Installation:

### 1. Clone the repository:
git clone [https://github.com/MRehan516/codedna-core.git](https://github.com/MRehan516/codedna-core.git)
cd codedna-core
### 2. Create and activate a virtual environment:
python -m venv .venv
source .venv/bin/activate  (On Windows use: .venv\Scripts\activate)
### 3. Install dependencies:
pip install -r requirements.txt
### 4. Configure environment variables:
Copy .env.example to .env and add your Supabase credentials:
SUPABASE_URL=[https://your-project-id.supabase.co](https://www.google.com/search?q=https://your-project-id.supabase.co)
SUPABASE_ANON_KEY=your-anon-key
CODEDNA_WATCH_DIR=.

## Running the Engine:
You need two terminal windows running simultaneously:

### Terminal 1: Start the Watcher Daemon
python -m capture.watcher

### Terminal 2: Start the Cloud Ingestor
python -m capture.ingestor

(Optional) Seed the database with 30 days of realistic demo telemetry:
python seed_demo.py

# **The Provenance Ledger:**
CodeDNA includes a Git hook (hooks/pre-commit) that intercepts commits, reads unsynced events from the local SQLite buffer, and writes a cryptographic .codedna/manifest.json sidecar file into the commit. This ensures every AI insertion is permanently anchored to your git history.
