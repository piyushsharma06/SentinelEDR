"""Host system identification and health collector."""

import json
import os
import platform
import socket
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import psutil


def get_or_create_stable_host_id(cache_path: str = "agent_cache.json") -> str:
    """
    Retrieve or create a stable host UUID persisted on disk across agent restarts.
    """
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "host_id" in data and data["host_id"]:
                    return data["host_id"]
        except Exception:
            pass

    # Generate new stable host ID
    new_host_id = f"HOST-{uuid.uuid4().hex[:12].upper()}"
    try:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump({"host_id": new_host_id, "created_at": datetime.now(timezone.utc).isoformat()}, f)
    except Exception:
        pass

    return new_host_id


def get_system_metadata() -> Dict[str, Any]:
    """Collect non-invasive host architecture and platform metadata."""
    hostname = socket.gethostname()
    ip_addrs: List[str] = []

    try:
        for iface_addrs in psutil.net_if_addrs().values():
            for addr in iface_addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                    ip_addrs.append(addr.address)
    except Exception:
        pass

    return {
        "hostname": hostname,
        "os_platform": platform.system(),
        "os_version": f"{platform.release()} ({platform.version()})",
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": psutil.cpu_count(logical=True),
        "total_memory_mb": round(psutil.virtual_memory().total / (1024 * 1024), 2),
        "ip_addresses": ip_addrs
    }


def collect_agent_health(
    host_id: str,
    consecutive_errors: int = 0,
    last_error: str = "",
    agent_version: str = "1.0.0"
) -> Dict[str, Any]:
    """Generate agent health telemetry event."""
    process = psutil.Process()
    mem_info = process.memory_info()

    status_str = "online"
    if consecutive_errors > 3:
        status_str = "degraded"
    elif consecutive_errors > 0:
        status_str = "warning"

    now_utc = datetime.now(timezone.utc)

    return {
        "event_uuid": f"HLT-{uuid.uuid4().hex[:16]}",
        "host_id": host_id,
        "event_type": "agent_health",
        "timestamp": now_utc.isoformat(),
        "schema_version": "1.0",
        "data": {
            "status": status_str,
            "agent_version": agent_version,
            "memory_usage_mb": round(mem_info.rss / (1024 * 1024), 2),
            "cpu_percent": process.cpu_percent(interval=None),
            "consecutive_collection_errors": consecutive_errors,
            "last_error_message": last_error,
            "hostname": socket.gethostname()
        }
    }
