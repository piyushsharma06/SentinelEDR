"""Tests for incident workflow, investigations, notes, and audit logging."""


def test_incident_creation_and_notes(client, analyst_headers):
    """Verify analyst can create an incident and append investigation timeline notes."""
    # 1. Create incident
    create_payload = {
        "title": "Investigating Suspicious PowerShell Beaconing",
        "description": "Office macro launched encoded command prompt.",
        "severity": "high",
        "assigned_to": "test_analyst",
        "alert_ids": []
    }
    create_resp = client.post("/api/v1/incidents", json=create_payload, headers=analyst_headers)
    assert create_resp.status_code == 201
    inc_data = create_resp.json()
    incident_id = inc_data["incident_id"]
    assert inc_data["status"] == "open"
    assert len(inc_data["investigation_notes"]) >= 1

    # 2. Add an investigation note
    update_payload = {
        "status": "investigating",
        "add_note": "Host disconnected from internal network. Forensic triage initiated."
    }
    update_resp = client.patch(f"/api/v1/incidents/{incident_id}", json=update_payload, headers=analyst_headers)
    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["status"] == "investigating"
    assert len(updated_data["investigation_notes"]) == 2
    assert "forensic triage" in updated_data["investigation_notes"][1]["text"].lower()

    # 3. Retrieve incident details
    get_resp = client.get(f"/api/v1/incidents/{incident_id}", headers=analyst_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["incident_id"] == incident_id


def test_audit_logs_recorded(client, admin_headers):
    """Verify state-changing analyst actions create immutable audit logs."""
    # Perform an action that logs an audit event
    client.post(
        "/api/v1/incidents",
        json={
            "title": "Audit Generation Test",
            "description": "Triggering audit event for verification.",
            "severity": "medium",
            "alert_ids": []
        },
        headers=admin_headers
    )

    resp = client.get("/api/v1/audit-logs", headers=admin_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert len(data["items"]) > 0
    # Verify audit record schema
    first = data["items"][0]
    assert "actor_username" in first
    assert "action" in first
    assert "resource_type" in first
    assert "timestamp" in first
