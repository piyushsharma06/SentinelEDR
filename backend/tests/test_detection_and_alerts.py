"""Tests for YAML detection rules, engine evaluation, alert creation, and deduplication."""

from datetime import datetime, timezone


def test_rule_a_parent_child_match(client, admin_headers):
    """Verify Rule A fires when winword.exe spawns powershell.exe."""
    payload = {
        "events": [
            {
                "event_uuid": "EVT-TEST-RULE-A-01",
                "host_id": "HOST-TEST-DET-01",
                "event_type": "process_creation",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "process_name": "powershell.exe",
                    "process_id": 9999,
                    "parent_process_name": "winword.exe",
                    "parent_process_id": 4444,
                    "command_line": "powershell.exe -NoProfile",
                    "username": "SENTINEL\\victim"
                }
            }
        ]
    }
    resp = client.post("/api/v1/events", json=payload, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["alerts_generated"] >= 1

    # Verify alert exists in API
    alerts_resp = client.get("/api/v1/alerts?rule_id=RULE-001-PARENT-CHILD", headers=admin_headers)
    assert alerts_resp.status_code == 200
    items = alerts_resp.json()["items"]
    assert len(items) > 0
    assert items[0]["rule_id"] == "RULE-001-PARENT-CHILD"
    assert items[0]["severity"] == "high"


def test_rule_b_script_cli_indicators(client, admin_headers):
    """Verify Rule B fires when powershell uses encoded command flags."""
    payload = {
        "events": [
            {
                "event_uuid": "EVT-TEST-RULE-B-01",
                "host_id": "HOST-TEST-DET-02",
                "event_type": "process_creation",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "process_name": "powershell.exe",
                    "command_line": "powershell.exe -WindowStyle Hidden -enc SQBFAFgA...",
                    "username": "SENTINEL\\victim"
                }
            }
        ]
    }
    resp = client.post("/api/v1/events", json=payload, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["alerts_generated"] >= 1


def test_rule_c_unusual_execution_context(client, admin_headers):
    """Verify Rule C fires when executable launches from Temp folder."""
    payload = {
        "events": [
            {
                "event_uuid": "EVT-TEST-RULE-C-01",
                "host_id": "HOST-TEST-DET-03",
                "event_type": "process_creation",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "process_name": "stager.exe",
                    "process_path": "C:\\Users\\user\\AppData\\Local\\Temp\\stager.exe",
                    "command_line": "\"C:\\Users\\user\\AppData\\Local\\Temp\\stager.exe\"",
                    "username": "SENTINEL\\user"
                }
            }
        ]
    }
    resp = client.post("/api/v1/events", json=payload, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["alerts_generated"] >= 1


def test_rule_d_suspicious_network(client, admin_headers):
    """Verify Rule D fires on outbound network socket from shell."""
    payload = {
        "events": [
            {
                "event_uuid": "EVT-TEST-RULE-D-01",
                "host_id": "HOST-TEST-DET-04",
                "event_type": "network_connection",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "process_name": "powershell.exe",
                    "process_id": 8888,
                    "local_address": "10.0.0.5",
                    "local_port": 50123,
                    "remote_address": "203.0.113.55",
                    "remote_port": 443,
                    "protocol": "tcp"
                }
            }
        ]
    }
    resp = client.post("/api/v1/events", json=payload, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["alerts_generated"] >= 1


def test_rule_e_monitored_directory(client, admin_headers):
    """Verify Rule E fires on ransomware extension in monitored directory."""
    payload = {
        "events": [
            {
                "event_uuid": "EVT-TEST-RULE-E-01",
                "host_id": "HOST-TEST-DET-05",
                "event_type": "file_activity",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "file_path": "C:\\Monitored\\important_database.db.locked",
                    "action": "created",
                    "file_size": 1024
                }
            }
        ]
    }
    resp = client.post("/api/v1/events", json=payload, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["alerts_generated"] >= 1


def test_rule_f_agent_health(client, admin_headers):
    """Verify Rule F fires on degraded agent health."""
    payload = {
        "events": [
            {
                "event_uuid": "EVT-TEST-RULE-F-01",
                "host_id": "HOST-TEST-DET-06",
                "event_type": "agent_health",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "status": "degraded",
                    "consecutive_collection_errors": 5,
                    "agent_version": "1.0.0"
                }
            }
        ]
    }
    resp = client.post("/api/v1/events", json=payload, headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["alerts_generated"] >= 1


def test_alert_deduplication_window(client, admin_headers):
    """Verify consecutive events matching the same rule and host deduplicate."""
    host_id = "HOST-TEST-DEDUP-01"
    event1 = {
        "event_uuid": "EVT-DEDUP-01",
        "host_id": host_id,
        "event_type": "process_creation",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {
            "process_name": "cmd.exe",
            "parent_process_name": "excel.exe"
        }
    }
    event2 = {
        "event_uuid": "EVT-DEDUP-02",
        "host_id": host_id,
        "event_type": "process_creation",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {
            "process_name": "cmd.exe",
            "parent_process_name": "excel.exe"
        }
    }

    client.post("/api/v1/events", json={"events": [event1]}, headers=admin_headers)
    client.post("/api/v1/events", json={"events": [event2]}, headers=admin_headers)

    resp = client.get(f"/api/v1/alerts?host_id={host_id}&rule_id=RULE-001-PARENT-CHILD", headers=admin_headers)
    assert resp.status_code == 200
    items = resp.json()["items"]
    # Only 1 unique alert should exist, but event_count should be 2!
    assert len(items) == 1
    assert items[0]["event_count"] == 2


def test_alert_lifecycle_status_and_false_positive(client, analyst_headers):
    """Verify analyst can triage alert and mark as false positive with rationale."""
    # Find any alert
    alerts_resp = client.get("/api/v1/alerts?page_size=1", headers=analyst_headers)
    items = alerts_resp.json()["items"]
    if not items:
        return
    alert_id = items[0]["alert_id"]

    # Patch status to false_positive
    patch_resp = client.patch(
        f"/api/v1/alerts/{alert_id}",
        json={
            "status": "false_positive",
            "false_positive_reason": "Verified legitimate internal administrative script."
        },
        headers=analyst_headers
    )
    assert patch_resp.status_code == 200
    updated = patch_resp.json()
    assert updated["status"] == "false_positive"
    assert "legitimate" in updated["false_positive_reason"].lower()
