"""Persistent, bounded SQLite-backed disk queue for offline event buffering."""

import json
import sqlite3
import threading
from typing import Any, Dict, List, Tuple


class PersistentEventQueue:
    """Thread-safe SQLite persistent FIFO event queue with bounded storage."""

    def __init__(self, db_path: str = "agent_queue.db", max_items: int = 2000):
        self.db_path = db_path
        self.max_items = max_items
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS event_queue (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_uuid TEXT UNIQUE,
                        event_payload TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()

    def enqueue(self, event_dict: Dict[str, Any]) -> bool:
        """Enqueue an event. If max_items exceeded, prune oldest items to bound disk usage."""
        event_uuid = event_dict.get("event_uuid", "")
        payload_str = json.dumps(event_dict)

        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check queue size and enforce bounds
                cursor.execute("SELECT COUNT(*) FROM event_queue")
                count = cursor.fetchone()[0]

                if count >= self.max_items:
                    # Prune oldest 10%
                    prune_count = max(1, self.max_items // 10)
                    cursor.execute(
                        "DELETE FROM event_queue WHERE id IN (SELECT id FROM event_queue ORDER BY id ASC LIMIT ?)",
                        (prune_count,)
                    )

                try:
                    cursor.execute(
                        "INSERT OR IGNORE INTO event_queue (event_uuid, event_payload) VALUES (?, ?)",
                        (event_uuid, payload_str)
                    )
                    conn.commit()
                    return True
                except sqlite3.Error:
                    return False

    def enqueue_batch(self, events: List[Dict[str, Any]]) -> int:
        """Enqueue multiple events efficiently."""
        enqueued = 0
        for ev in events:
            if self.enqueue(ev):
                enqueued += 1
        return enqueued

    def peek_batch(self, limit: int = 50) -> List[Tuple[int, Dict[str, Any]]]:
        """Fetch the next batch of events without removing them."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, event_payload FROM event_queue ORDER BY id ASC LIMIT ?",
                    (limit,)
                )
                rows = cursor.fetchall()
                results = []
                for row_id, payload_str in rows:
                    try:
                        results.append((row_id, json.loads(payload_str)))
                    except json.JSONDecodeError:
                        continue
                return results

    def acknowledge_batch(self, ids: List[int]) -> int:
        """Delete acknowledged events after successful delivery to the backend."""
        if not ids:
            return 0
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                placeholders = ",".join("?" for _ in ids)
                cursor.execute(f"DELETE FROM event_queue WHERE id IN ({placeholders})", ids)
                conn.commit()
                return cursor.rowcount

    def size(self) -> int:
        """Return total unacknowledged event count in the queue."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM event_queue")
                return cursor.fetchone()[0]
