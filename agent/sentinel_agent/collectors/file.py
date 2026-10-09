"""Opt-in file activity collector strictly targeting a designated test directory."""

import logging
import os
import queue
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

logger = logging.getLogger(__name__)


class SafeFileEventHandler(FileSystemEventHandler):
    """Captures file change metadata without reading or uploading file contents."""

    def __init__(self, host_id: str, event_queue: queue.Queue):
        super().__init__()
        self.host_id = host_id
        self.event_queue = event_queue

    def _create_event(self, action: str, src_path: str) -> None:
        if os.path.isdir(src_path):
            return

        now_utc = datetime.now(timezone.utc)
        file_size = 0
        try:
            if os.path.exists(src_path):
                file_size = os.path.getsize(src_path)
        except Exception:
            file_size = 0

        ext = Path(src_path).suffix.lower()

        event = {
            "event_uuid": f"EVT-FILE-{uuid.uuid4().hex[:16]}",
            "host_id": self.host_id,
            "event_type": "file_activity",
            "timestamp": now_utc.isoformat(),
            "schema_version": "1.0",
            "data": {
                "file_path": str(src_path),
                "file_name": os.path.basename(src_path),
                "extension": ext,
                "file_size": file_size,
                "action": action
            }
        }
        self.event_queue.put(event)

    def on_created(self, event: FileSystemEvent):
        self._create_event("created", event.src_path)

    def on_modified(self, event: FileSystemEvent):
        self._create_event("modified", event.src_path)

    def on_deleted(self, event: FileSystemEvent):
        self._create_event("deleted", event.src_path)

    def on_moved(self, event: FileSystemEvent):
        dest = getattr(event, "dest_path", event.src_path)
        self._create_event("renamed", dest)


class DirectoryWatcher:
    """Manages background directory monitoring for a designated safe test directory."""

    def __init__(self, host_id: str, monitored_directory: str):
        self.host_id = host_id
        self.monitored_directory = os.path.abspath(monitored_directory)
        self._events: queue.Queue = queue.Queue(maxsize=1000)
        self.observer: Optional[Observer] = None

    def start(self):
        """Start watchdog observer thread."""
        os.makedirs(self.monitored_directory, exist_ok=True)
        handler = SafeFileEventHandler(self.host_id, self._events)
        self.observer = Observer()
        self.observer.schedule(handler, self.monitored_directory, recursive=True)
        self.observer.daemon = True
        self.observer.start()
        logger.info(f"Safe file monitoring active on directory: {self.monitored_directory}")

    def collect(self) -> List[Dict[str, Any]]:
        """Drain accumulated file events from the thread queue."""
        events = []
        while not self._events.empty():
            try:
                events.append(self._events.get_nowait())
            except queue.Empty:
                break
        return events

    def stop(self):
        """Stop background watcher observer."""
        if self.observer:
            try:
                self.observer.stop()
                self.observer.join(timeout=2.0)
            except Exception:
                pass
