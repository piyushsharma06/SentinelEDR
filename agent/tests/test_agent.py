"""Tests for Windows endpoint agent components: collectors, queue, and configuration."""

import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sentinel_agent")))

from sentinel_agent.config import AgentConfig
from sentinel_agent.queue import PersistentEventQueue
from sentinel_agent.collectors.system import (
    get_or_create_stable_host_id,
    get_system_metadata,
    collect_agent_health
)
from sentinel_agent.collectors.process import ProcessCollector
from sentinel_agent.collectors.network import NetworkCollector


def test_agent_config_safe_defaults():
    """Verify safe configuration defaults and validation."""
    config = AgentConfig()
    assert config.backend_url == "http://127.0.0.1:8000"
    assert config.file_monitoring_enabled is False
    assert config.max_queue_items == 2000


def test_agent_config_rejects_unsafe_root_directories():
    """Verify agent rejects monitoring critical OS root paths."""
    with pytest.raises(ValueError, match="root or system directory"):
        AgentConfig(monitored_directory="C:\\Windows")

    with pytest.raises(ValueError, match="root or system directory"):
        AgentConfig(monitored_directory="C:\\")


def test_persistent_event_queue_bounds_and_fifo():
    """Verify SQLite queue enforces bounds and provides FIFO batching."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_queue.db")

    try:
        max_limit = 10
        queue = PersistentEventQueue(db_path=db_path, max_items=max_limit)

        # Enqueue 15 events into a queue bounded at 10
        for i in range(15):
            queue.enqueue({"event_uuid": f"EVT-Q-{i}", "val": i})

        # Queue should be bounded to <= max_limit
        assert queue.size() <= max_limit

        # Peek batch of 5
        batch = queue.peek_batch(limit=5)
        assert len(batch) == 5
        row_ids = [item[0] for item in batch]

        # Acknowledge and remove batch
        ack_count = queue.acknowledge_batch(row_ids)
        assert ack_count == 5
        assert queue.size() == (10 - 5)
    finally:
        import shutil
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


def test_stable_host_id_persistence():
    """Verify host ID persists across multiple calls."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        cache_path = tmp.name

    try:
        id1 = get_or_create_stable_host_id(cache_path=cache_path)
        id2 = get_or_create_stable_host_id(cache_path=cache_path)
        assert id1 == id2
        assert id1.startswith("HOST-")
    finally:
        if os.path.exists(cache_path):
            os.remove(cache_path)


def test_system_metadata_collection():
    """Verify system collector collects valid OS metadata without invasive permissions."""
    meta = get_system_metadata()
    assert "hostname" in meta
    assert "os_platform" in meta
    assert "total_memory_mb" in meta
    assert meta["total_memory_mb"] > 0


def test_agent_health_event_structure():
    """Verify health telemetry event schema."""
    health_evt = collect_agent_health(
        host_id="HOST-TEST-01",
        consecutive_errors=0,
        last_error=""
    )
    assert health_evt["event_type"] == "agent_health"
    assert health_evt["host_id"] == "HOST-TEST-01"
    assert health_evt["data"]["status"] == "online"
    assert "memory_usage_mb" in health_evt["data"]


def test_process_collector_graceful_execution():
    """Verify process collector executes and returns normalized events safely."""
    collector = ProcessCollector(host_id="HOST-TEST-PROC")
    events = collector.collect()
    assert isinstance(events, list)
    # Consecutive call should yield empty or minimal events because of deduplication cache
    subsequent = collector.collect()
    assert len(subsequent) <= len(events)


def test_network_collector_graceful_execution():
    """Verify network collector handles socket enumeration without crashing."""
    collector = NetworkCollector(host_id="HOST-TEST-NET")
    events = collector.collect()
    assert isinstance(events, list)
