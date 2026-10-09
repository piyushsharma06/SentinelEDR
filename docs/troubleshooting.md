# SentinelEDR Troubleshooting & Diagnostics Guide

Common diagnostic scenarios and step-by-step resolution procedures.

---

## 1. Backend Diagnostics

### Port 8000 Already in Use
If starting Uvicorn fails with `[Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)`:

```powershell
# Identify process holding port 8000
netstat -ano | findstr :8000

# Start SentinelEDR on an alternate port
python -m uvicorn app.main:app --app-dir backend --port 8001
```

### Database Inconsistencies or Stale SQLite File
To reset the development SQLite database cleanly:

```powershell
# Remove local database file
Remove-Item sentinel.db -Force

# Re-seed demo data and synchronize rules
python -c "import sys; sys.path.insert(0, 'backend'); import app.demo.seed; app.demo.seed.main()"
```

---

## 2. Windows Agent Diagnostics

### Agent Reports `backend_reachable: false`
Run the status command:
```powershell
python -m sentinel_agent.main --config agent/config.yaml --status
```
1. Verify the backend process is running: `curl http://127.0.0.1:8000/health`.
2. Check `agent/config.yaml` to ensure `backend_url` is configured correctly.
3. Check Windows Firewall or local proxy settings.

### Network Socket Access Denied
On Windows, standard user accounts cannot inspect elevated system sockets (e.g., LSASS or System idle processes).
- **Behavior:** The agent logs a debug message and gracefully continues collecting permitted user-level process sockets.
- **Resolution:** If elevated socket visibility is desired in a lab VM, open PowerShell with **"Run as Administrator"** and launch the agent.

---

## 3. Frontend Diagnostics

### CORS Request Blocked
If the browser console displays a Cross-Origin Resource Sharing (CORS) error:
1. Check `.env` or `backend/app/config.py` for `CORS_ORIGINS`.
2. Ensure your frontend origin (e.g., `http://localhost:5173` or `http://localhost:3000`) is in the allowed origins list.

### Session Expired / Token Invalid
If navigation continuously bounces back to `/login`:
1. Clear browser localStorage: `localStorage.clear()`.
2. Log in again with `admin` / `SentinelAdmin!2026Secure`.
