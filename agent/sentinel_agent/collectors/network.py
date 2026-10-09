"""Network connection collector."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Set, Tuple
import psutil

logger = logging.getLogger(__name__)


class NetworkCollector:
    """Monitors active socket connections, reporting newly established remote connections."""

    def __init__(self, host_id: str):
        self.host_id = host_id
        # Set of connection tuples: (protocol, local_ip, local_port, remote_ip, remote_port, pid)
        self._seen_connections: Set[Tuple[str, str, int, str, int, int]] = set()

    def collect(self) -> List[Dict[str, Any]]:
        """Poll network sockets and return normalized network_connection events."""
        events: List[Dict[str, Any]] = []
        current_seen: Set[Tuple[str, str, int, str, int, int]] = set()
        now_utc = datetime.now(timezone.utc)

        try:
            connections = psutil.net_connections(kind="inet")
        except (psutil.AccessDenied, PermissionError):
            logger.debug("Access denied inspecting socket connections (requires elevated privileges).")
            return []
        except Exception as e:
            logger.debug(f"Error enumerating socket connections: {e}")
            return []

        for conn in connections:
            try:
                # We are primarily interested in outbound connections with remote endpoints
                if not conn.raddr:
                    continue

                proto = "tcp" if conn.type == 1 else "udp"
                local_ip = conn.laddr.ip if conn.laddr else ""
                local_port = conn.laddr.port if conn.laddr else 0
                remote_ip = conn.raddr.ip if conn.raddr else ""
                remote_port = conn.raddr.port if conn.raddr else 0
                pid = conn.pid or 0

                # Filter out pure loopbacks
                if remote_ip in ("127.0.0.1", "::1", "0.0.0.0"):
                    continue

                ident = (proto, local_ip, local_port, remote_ip, remote_port, pid)
                current_seen.add(ident)

                if ident in self._seen_connections:
                    continue

                # Lookup process name if pid is available
                proc_name = ""
                if pid:
                    try:
                        p = psutil.Process(pid)
                        proc_name = p.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        proc_name = ""

                event = {
                    "event_uuid": f"EVT-NET-{uuid.uuid4().hex[:16]}",
                    "host_id": self.host_id,
                    "event_type": "network_connection",
                    "timestamp": now_utc.isoformat(),
                    "schema_version": "1.0",
                    "data": {
                        "process_id": pid,
                        "process_name": proc_name,
                        "local_address": local_ip,
                        "local_port": local_port,
                        "remote_address": remote_ip,
                        "remote_port": remote_port,
                        "protocol": proto,
                        "status": conn.status
                    }
                }
                events.append(event)

            except Exception:
                continue

        self._seen_connections = current_seen
        return events
