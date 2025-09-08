import os
import threading
import queue
import time
import sqlite3
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pydantic import BaseModel, ValidationError, Field
from typing import Optional

# Configure your log files here
LOG_FILES = {
    "mouse": "mouse_events.jsonl",
    "keyboard": "keyboard_events.jsonl",
    "process": "user_process_events.jsonl",
}

DB_FILE = "events.db"

# -------------------------
# Define Pydantic Schemas
# -------------------------
class Position(BaseModel):
    x: float
    y: float

class MouseEvent(BaseModel):
    timestamp: float
    event: str
    position: Optional[Position] = None
    button: Optional[str] = None
    pressed: Optional[bool] = None
    scroll: Optional[dict] = None

class KeyboardEvent(BaseModel):
    timestamp: float
    event: str
    key: str

class ProcessEvent(BaseModel):
    timestamp: float
    event: str
    process: dict

# Map source to schema for dynamic validation
SCHEMA_MAP = {
    "mouse": MouseEvent,
    "keyboard": KeyboardEvent,
    "process": ProcessEvent,
}

# -------------------------
# Database setup and utils
# -------------------------
class EventDB:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.lock = threading.Lock()
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                timestamp REAL NOT NULL,
                event TEXT NOT NULL,
                data TEXT
            )
            """)

    def bulk_insert(self, records):
        with self.lock:
            with self.conn:
                self.conn.executemany(
                    "INSERT INTO events (source, timestamp, event, data) VALUES (?, ?, ?, ?)",
                    records
                )

    def close(self):
        self.conn.close()

# -------------------------
# File watching ingestion
# -------------------------
class LogFileHandler(FileSystemEventHandler):
    def __init__(self, source: str, filepath: str, line_queue: queue.Queue):
        self.source = source
        self.filepath = filepath
        self.line_queue = line_queue
        self.file = open(filepath, "r", encoding="utf-8")
        # Move to the end so we only process new lines
        self.file.seek(0, os.SEEK_END)

    def on_modified(self, event):
        if event.src_path.endswith(self.filepath): # type: ignore
            for line in self.file:
                line = line.strip()
                if line:
                    self.line_queue.put((self.source, line))

# -------------------------
# Worker thread handles parsing and batch insert
# -------------------------
class IngestionWorker(threading.Thread):
    def __init__(self, db: EventDB, line_queue: queue.Queue, batch_size=100, flush_interval=5):
        super().__init__(daemon=True)
        self.db = db
        self.line_queue = line_queue
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.buffer = []
        self.last_flush = time.time()

    def run(self):
        while True:
            try:
                item = self.line_queue.get(timeout=1)
            except queue.Empty:
                item = None

            now = time.time()
            if item is not None:
                source, line = item
                try:
                    event_obj = SCHEMA_MAP[source].parse_raw(line)
                    record = (source, event_obj.timestamp, event_obj.event, line)
                    self.buffer.append(record)
                except ValidationError as e:
                    print(f"[ERROR] Validation failed for source `{source}` line: {line}\n{e}")
                except Exception as e:
                    print(f"[ERROR] Unexpected error parsing line: {line}\n{e}")

            # Flush if buffer full or flush interval passed
            if len(self.buffer) >= self.batch_size or (now - self.last_flush) >= self.flush_interval:
                if self.buffer:
                    try:
                        self.db.bulk_insert(self.buffer)
                        #print(f"[INFO] Inserted {len(self.buffer)} records into DB")
                        self.buffer.clear()
                    except Exception as e:
                        print(f"[ERROR] Failed to insert batch into DB: {e}")
                self.last_flush = now

# -------------------------
# Start the ingestion service
# -------------------------
def main():
    print("Starting Robust Ingestion Service...")
    line_queue = queue.Queue(maxsize=10000)
    db = EventDB(DB_FILE)

    observer = Observer()
    for source, filepath in LOG_FILES.items():
        if not os.path.exists(filepath):
            # Create empty file if missing
            open(filepath, "a").close()
        handler = LogFileHandler(source, filepath, line_queue)
        observer.schedule(handler, ".", recursive=False)

    observer.start()
    print("Watching log files for new events...")

    # Start worker thread
    worker = IngestionWorker(db, line_queue)
    worker.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping ingestion service...")
        observer.stop()
        observer.join()
        db.close()

if __name__ == "__main__":
    main()
