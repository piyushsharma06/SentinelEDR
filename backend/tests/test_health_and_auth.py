"""Tests for health check, authentication, RBAC, and agent enrollment."""

from app.config import settings


def test_health_endpoint(client):
    """Verify health endpoint reports healthy database status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "SentinelEDR"


def test_auth_login_success(client):
    """Verify analyst authentication produces valid JWT access token."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_analyst", "password": "AnalystSecret!2026"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "test_analyst"
    assert data["user"]["role"] == "analyst"


def test_auth_login_wrong_password(client):
    """Verify incorrect credentials are rejected with HTTP 401."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_analyst", "password": "WrongPassword123"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()


def test_auth_login_deactivated_account(client):
    """Verify deactivated accounts cannot log in."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "test_deactivated", "password": "DeactivatedSecret!2026"}
    )
    assert response.status_code == 403


def test_auth_me_profile(client, analyst_headers):
    """Verify me endpoint returns user identity from valid token."""
    response = client.get("/api/v1/auth/me", headers=analyst_headers)
    assert response.status_code == 200
    assert response.json()["username"] == "test_analyst"


def test_auth_me_unauthorized(client):
    """Verify me endpoint rejects requests without token."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_agent_enrollment_success(client):
    """Verify agent enrollment with valid pre-shared token issues an API key."""
    response = client.post(
        "/api/v1/auth/enroll-agent",
        json={
            "host_id": "HOST-TEST-AGENT-01",
            "hostname": "TEST-WIN11-WS",
            "os_platform": "Windows",
            "os_version": "11 23H2",
            "agent_version": "1.0.0",
            "enrollment_token": settings.agent_enrollment_token
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["host_id"] == "HOST-TEST-AGENT-01"
    assert data["api_key"].startswith("sentinel_agent_")


def test_agent_enrollment_invalid_token(client):
    """Verify enrollment fails if enrollment token is incorrect."""
    response = client.post(
        "/api/v1/auth/enroll-agent",
        json={
            "host_id": "HOST-TEST-AGENT-02",
            "hostname": "TEST-WIN11-WS",
            "os_platform": "Windows",
            "agent_version": "1.0.0",
            "enrollment_token": "wrong-invalid-enrollment-key"
        }
    )
    assert response.status_code == 403
