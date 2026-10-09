"""Process creation and execution collector."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Tuple
import psutil

logger = logging.getLogger(__name__)


class ProcessCollector:
    """Monitors running processes, tracking seen process instances to emit newly created processes."""

    def __init__(self, host_id: str):
        self.host_id = host_id
        # Set of (pid, create_time) to avoid duplicate event flooding
        self._seen_processes: Set[Tuple[int, float]] = set()
        self._initialized = False

    def collect(self) -> List[Dict[str, Any]]:
        """
        Poll processes and return normalized process_creation events for newly observed processes.
        """
        events: List[Dict[str, Any]] = []
        current_seen: Set[Tuple[int, float]] = set()

        for proc in psutil.process_iter(['pid', 'ppid', 'name', 'exe', 'cmdline', 'username', 'create_time']):
            try:
                info = proc.info
                pid = info['pid']
                create_time = info['create_time'] or 0.0
                ident = (pid, create_time)
                current_seen.add(ident)

                if ident in self._seen_processes:
                    continue

                # Collect parent process name if accessible
                ppid = info.get('ppid')
                parent_name = None
                if ppid:
                    try:
                        parent = psutil.Process(ppid)
                        parent_name = parent.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        parent_name = None

                # Format commandline
                cmdline_list = info.get('cmdline') or []
                cmdline_str = " ".join(cmdline_list) if cmdline_list else (info.get('exe') or info.get('name') or "")

                # Convert create_time to UTC ISO timestamp
                event_ts = datetime.fromtimestamp(create_time, tz=timezone.utc).isoformat() if create_time else datetime.now(timezone.utc).isoformat()

                event = {
                    "event_uuid": f"EVT-PROC-{uuid.uuid4().hex[:16]}",
                    "host_id": self.host_id,
                    "event_type": "process_creation",
                    "timestamp": event_ts,
                    "schema_version": "1.0",
                    "data": {
                        "process_id": pid,
                        "parent_process_id": ppid,
                        "process_name": info.get('name') or "",
                        "process_path": info.get('exe') or "",
                        "parent_process_name": parent_name,
                        "command_line": cmdline_str,
                        "username": info.get('username') or "",
                        "create_time": create_time
                    }
                }
                events.append(event)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                logger.debug(f"Error inspecting process {proc.pid}: {e}")
                continue

        # On initial run, we mark current state as seen to avoid blasting thousands of baseline boot processes,
        # or we report a sampled baseline. Let's record all current seen processes.
        self._seen_processes = current_seen
        return events
