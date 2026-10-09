# SentinelEDR Deployment & Operations Guide

SentinelEDR supports two deployment workflows:
1. **Local Development:** SQLite + Uvicorn + Vite Dev Server (fastest setup, zero container dependencies)
2. **Containerized Production Stack:** Docker Compose + PostgreSQL + FastAPI + Nginx React Frontend

---

## 1. Local Development Setup (Quick Start)

### Step 1: Install Python & Node Packages
```powershell
pip install -r backend/requirements.txt
pip install -r agent/requirements.txt
cd frontend && npm install && cd ..
```

### Step 2: Seed Synthetic Demo Data & Sync Rules
```powershell
python -c "import sys; sys.path.insert(0, 'backend'); import app.demo.seed; app.demo.seed.main()"
```

### Step 3: Start FastAPI Backend Server
```powershell
python -m uvicorn app.main:app --app-dir backend --reload --port 8000 --host 127.0.0.1
```
The backend API is now live at `http://127.0.0.1:8000` (OpenAPI docs at `/docs`).

### Step 4: Start React Frontend Development Server
In a new terminal:
```powershell
cd frontend
npm run dev
```
Open `http://localhost:5173` in your browser. Log in using `admin` / `SentinelAdmin!2026Secure`.

---

## 2. Containerized Deployment with Docker Compose

SentinelEDR includes production-ready Dockerfiles and `compose.yaml`:

### Architecture in Docker Compose:
- **`sentinel-postgres`:** PostgreSQL 16 Alpine with internal bridge network. The database port is not exposed to the public host interface.
- **`sentinel-backend`:** Multi-worker Uvicorn application running as non-root user `sentinel`. Health checked at `/health`.
- **`sentinel-frontend`:** Multi-stage Nginx container serving compiled static assets on port `3000`.

### Commands:

```powershell
# Build and start all services in the background
docker compose up --build -d

# Check service health and running status
docker compose ps

# View application logs
docker compose logs -f backend

# Stop the stack
docker compose down
```

Access the frontend dashboard at `http://localhost:3000` and the API at `http://localhost:8000`.

---

## 3. Production Hardening Checklist

When deploying SentinelEDR beyond a local development lab:

1. **Rotate Default Secrets:** Generate a 64-character random string for `JWT_SECRET_KEY` and change `BOOTSTRAP_ADMIN_PASSWORD` in `.env`.
2. **Enable HTTPS:** Place an SSL/TLS terminating reverse proxy (such as Caddy, Traefik, or Cloudflare Tunnel) in front of the application.
3. **CORS Restrictions:** Restrict `CORS_ORIGINS` strictly to your domain.
4. **Agent Network Binding:** Ensure agents communicate over secure HTTPS endpoints with verified certificates.
