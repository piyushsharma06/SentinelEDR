# SentinelEDR REST API Reference

The SentinelEDR API exposes RESTful endpoints with OpenAPI 3.0 documentation accessible at `http://127.0.0.1:8000/docs` in development mode.

## 1. Authentication Scheme

SentinelEDR enforces strict separation between analyst and agent credentials:

1. **Analyst Access:**
   - Header: `Authorization: Bearer <jwt_token>`
   - Acquired via: `POST /api/v1/auth/login`
2. **Agent Telemetry Access:**
   - Header: `X-Agent-Key: sentinel_agent_<secret>`
   - Acquired via: `POST /api/v1/auth/enroll-agent`

---

## 2. API Endpoints

### 2.1 System & Statistics

#### `GET /health`
Returns system health, database connectivity status, and version.
```json
{
  "status": "healthy",
  "app": "SentinelEDR",
  "version": "1.0.0",
  "database": "connected",
  "demo_mode": true
}
```

#### `GET /api/v1/stats`
Returns aggregated security overview metrics for the SOC dashboard.
- **Auth:** Analyst Bearer Token

---

### 2.2 Authentication & Enrollment

#### `POST /api/v1/auth/login`
Authenticates an analyst user and returns an access token.
```json
// Request
{
  "username": "admin",
  "password": "SentinelAdmin!2026Secure"
}

// Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "expires_in": 7200,
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "is_active": true
  }
}
```

#### `POST /api/v1/auth/enroll-agent`
Enrolls a new Windows endpoint using the pre-shared enrollment token.
```json
// Request
{
  "host_id": "HOST-WIN11-001",
  "hostname": "FIN-WIN11-EXEC",
  "os_platform": "Windows",
  "agent_version": "1.0.0",
  "enrollment_token": "sentinel-agent-enrollment-secret-key-change-me"
}

// Response
{
  "host_id": "HOST-WIN11-001",
  "api_key": "sentinel_agent_e7f...",
  "message": "Agent enrolled successfully. Store this API key securely."
}
```

---

### 2.3 Endpoint Telemetry Ingestion

#### `POST /api/v1/events`
Submits a batch of normalized security events from an enrolled agent.
- **Auth:** `X-Agent-Key` header
- **Batch Limit:** 100 events

```json
// Request
{
  "events": [
    {
      "event_uuid": "EVT-PROC-12345678",
      "host_id": "HOST-WIN11-001",
      "event_type": "process_creation",
      "timestamp": "2026-10-10T00:30:00Z",
      "schema_version": "1.0",
      "data": {
        "process_name": "powershell.exe",
        "process_id": 4820,
        "parent_process_name": "winword.exe",
        "command_line": "powershell.exe -w hidden -enc ...",
        "username": "SENTINEL\\victim"
      }
    }
  ]
}

// Response
{
  "accepted": 1,
  "rejected": 0,
  "duplicates": 0,
  "alerts_generated": 1
}
```

---

### 2.4 Alert Triage

#### `GET /api/v1/alerts`
Retrieves paginated alerts with query filters (`severity`, `status`, `host_id`, `rule_id`, `search`, `page`, `page_size`).

#### `PATCH /api/v1/alerts/{alert_id}`
Updates alert status, assignment, or false-positive rationale.
```json
// Request
{
  "status": "false_positive",
  "false_positive_reason": "Verified legitimate internal administrative task."
}
```

---

### 2.5 Incident Management

#### `POST /api/v1/incidents`
Opens a new security incident case.
```json
// Request
{
  "title": "Suspected PowerShell Dropper on Financial Workstation",
  "description": "Macro spawned encoded shell connecting to external address.",
  "severity": "high",
  "assigned_to": "admin",
  "alert_ids": ["ALT-43FA7783"]
}
```

#### `PATCH /api/v1/incidents/{incident_id}`
Appends an investigation note or updates status (`open`, `investigating`, `contained`, `resolved`, `closed`).
```json
// Request
{
  "status": "contained",
  "add_note": "Host network quarantined. Memory dump captured for analysis."
}
```
