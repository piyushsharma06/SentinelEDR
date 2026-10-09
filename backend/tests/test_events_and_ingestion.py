"""Tests for event ingestion, agent credentials, and event explorer APIs."""

from datetime import datetime, timezone
from app.config import settings
from app.models.agent_credential import AgentCredential
from app.auth.security import generate_agent_api_key


def test_event_ingestion_with_agent_key(client, db_session):
    """Verify enrolled agent can submit valid event batch using X-Agent-Key header."""
    raw_key, key_hash, prefix = generate_agent_api_key()
    host_id = "HOST-INGEST-01"

    cred = AgentCredential(
        host_id=host_id,
        api_key_hash=key_hash,
        api_key_prefix=prefix,
        is_active=True
    )
    db_session.add(cred)
    db_session.commit()

    payload = {
        "events": [
            {
                "event_uuid": "EVT-TEST-BENIGN-01",
                "host_id": host_id,
                "event_type": "process_creation",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "schema_version": "1.0",
                "data": {
                    "process_name": "notepad.exe",
                    "process_id": 1234,
                    "parent_process_name": "explorer.exe",
                    "command_line": "notepad.exe text.txt",
                    "username": "SENTINEL\\user"
                }
            }
        ]
    }

    response = client.post(
        "/api/v1/events",
        json=payload,
        headers={"X-Agent-Key": raw_key}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["accepted"] == 1
    assert data["rejected"] == 0
    assert data["duplicates"] == 0
    # Benign notepad launch should not trigger alerts
    assert data["alerts_generated"] == 0


def test_event_ingestion_revoked_key(client, db_session):
    """Verify revoked agent API keys are rejected with HTTP 401."""
    raw_key, key_hash, prefix = generate_agent_api_key()
    host_id = "HOST-REVOKED-01"

    cred = AgentCredential(
        host_id=host_id,
        api_key_hash=key_hash,
        api_key_prefix=prefix,
        is_active=False,  # Revoked!
        revoked_at=datetime.now(timezone.utc)
    )
    db_session.add(cred)
    db_session.commit()

    payload = {
        "events": [
            {
                "event_uuid": "EVT-TEST-REVOKED-01",
                "host_id": host_id,
                "event_type": "process_creation",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {"process_name": "test.exe"}
            }
        ]
    }

    response = client.post(
        "/api/v1/events",
        json=payload,
        headers={"X-Agent-Key": raw_key}
    )
    assert response.status_code == 401
    assert "revoked" in response.json()["detail"].lower()


def test_event_ingestion_cross_host_spoofing_prevented(client, db_session):
    """Verify agent credential for Host A cannot submit events for Host B."""
    raw_key, key_hash, prefix = generate_agent_api_key()
    cred = AgentCredential(
        host_id="HOST-LEGIT-01",
        api_key_hash=key_hash,
        api_key_prefix=prefix,
        is_active=True
    )
    db_session.add(cred)
    db_session.commit()

    # Attempt to submit event spoofing HOST-SPOOFED-99
    payload = {
        "events": [
            {
                "event_uuid": "EVT-TEST-SPOOF-01",
                "host_id": "HOST-SPOOFED-99",
                "event_type": "process_creation",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {"process_name": "cmd.exe"}
            }
        ]
    }

    response = client.post(
        "/api/v1/events",
        json=payload,
        headers={"X-Agent-Key": raw_key}
    )
    assert response.status_code == 403


def test_event_ingestion_oversized_batch_rejected(client, admin_headers):
    """Verify batch exceeding event_ingestion_batch_limit is rejected with 413."""
    oversized = [
        {
            "event_uuid": f"EVT-OVER-{i}",
            "host_id": "HOST-BATCH-01",
            "event_type": "process_creation",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {"process_name": f"proc_{i}.exe"}
        }
        for i in range(settings.event_ingestion_batch_limit + 10)
    ]

    response = client.post(
        "/api/v1/events",
        json={"events": oversized},
        headers=admin_headers
    )
    assert response.status_code == 413


def test_event_query_pagination_and_filters(client, analyst_headers):
    """Verify GET /api/v1/events supports filtering and pagination."""
    response = client.get("/api/v1/events?page=1&page_size=10", headers=analyst_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "total_pages" in data
