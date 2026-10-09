# SentinelEDR Windows Endpoint Agent Setup Guide

This guide walks through configuring, enrolling, and running the SentinelEDR Windows Endpoint Agent on Windows 10 or 11.

## 1. Prerequisites

- Windows 10 (21H2+) or Windows 11
- Python 3.11, 3.12, 3.13, or 3.14
- Network connectivity to the SentinelEDR backend API (default: `http://127.0.0.1:8000`)

---

## 2. Installation

Open PowerShell as a standard user (or Administrator if you wish to inspect elevated system sockets):

```powershell
# Navigate to project root
cd c:\path\to\sentinel-edr

# Install agent dependencies
pip install -r agent/requirements.txt
```

---

## 3. Configuration

Copy the example configuration file:

```powershell
copy agent\config.example.yaml agent\config.yaml
```

Inspect `agent/config.yaml`:

```yaml
backend_url: "http://127.0.0.1:8000"
agent_api_key: "" # Leave blank to auto-enroll on first startup
enrollment_token: "sentinel-agent-enrollment-secret-key-change-me"
auto_enroll: true

process_poll_interval: 5
network_poll_interval: 10
health_interval: 30

queue_db_path: "agent_queue.db"
max_queue_items: 2000

file_monitoring_enabled: false
monitored_directory: "./monitored_test_dir"
```

---

## 4. Check Agent Status

Verify the agent can detect host metadata and evaluate connectivity:

```powershell
python -m sentinel_agent.main --config agent/config.yaml --status
```

Expected output:
```json
{
  "agent_version": "1.0.0",
  "host_id": "HOST-9711478D6547",
  "backend_url": "http://127.0.0.1:8000",
  "backend_reachable": true,
  "queue_depth": 0,
  "system_metadata": {
    "hostname": "MY-PC",
    "os_platform": "Windows",
    "os_version": "11 (10.0.26200)"
  }
}
```

---

## 5. Starting the Agent

Ensure the SentinelEDR backend is running on `http://127.0.0.1:8000`, then start the agent daemon:

```powershell
python -m sentinel_agent.main --config agent/config.yaml
```

The agent will:
1. Connect to the backend and auto-enroll using the enrollment token.
2. Receive a dedicated agent API key.
3. Start the process collector (ticking every 5 seconds).
4. Start the network connection collector (ticking every 10 seconds).
5. Deliver telemetry batches to `/api/v1/events`.

Press `Ctrl+C` at any time to initiate a clean, graceful shutdown.
