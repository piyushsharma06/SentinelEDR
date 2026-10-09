# SentinelEDR Security Model & Threat Boundaries

This document defines the security architecture, authorization model, privacy protections, and threat assumptions of SentinelEDR.

## 1. Threat Model & Product Scope

SentinelEDR is an **educational detection engineering and SOC simulation platform**. It is intended for:
- Blue team defense exercises
- Learning threat detection rule writing
- Demonstrating incident response workflows in a controlled sandbox

**Explicit Non-Goals:**
- SentinelEDR does not replace commercial enterprise EDR agents (e.g., CrowdStrike Falcon, Microsoft Defender for Endpoint).
- SentinelEDR does NOT execute automated destructive remediation (process killing, file deletion, machine network isolation) in this version to eliminate the risk of accidental host disruption.

---

## 2. Authentication & Authorization Architecture

### 2.1 Role-Based Access Control (RBAC)

| Role | Permissions |
| :--- | :--- |
| **Admin** | Full system access: manage analyst users, toggle detection rules, seed/reset demo data, enroll/revoke agent credentials, triage alerts, manage incidents. |
| **Analyst** | Operational SOC access: view overview metrics, triage alerts, update alert status, mark false positives, create and update incidents, post investigation notes. |
| **Viewer** | Read-only access: view dashboard, endpoint inventory, event explorer, alerts, and incident cases. |

### 2.2 Credential Protection & Storage

- **Analyst Passwords:** Hashed using **PBKDF2-HMAC-SHA256** with 200,000 iterations and cryptographically random 16-byte salts.
- **Agent API Keys:** Formatted as `sentinel_agent_<token_urlsafe(32)>`. The raw key is only returned once upon enrollment. The database stores only the SHA-256 hash and a 16-character prefix for UI identification.
- **Credential Separation:** Agent credentials are systematically rejected on analyst endpoints, and analyst JWTs cannot be used to submit telemetry batches.

---

## 3. Telemetry Ingestion Protections

1. **Host Spoofing Defense:** When an agent submits a batch to `POST /api/v1/events`, the server validates that every `event.host_id` matches the `host_id` assigned to that API key. Mismatches are rejected with HTTP 403.
2. **Payload Size Bounds:** Ingestion enforces a hard ceiling of 100 events per request batch. Oversized payloads are rejected with HTTP 413 to prevent memory denial-of-service.
3. **Queue Bounds:** The local agent queue is capped at 2,000 items on disk to prevent uncontrolled disk storage consumption during prolonged network partitions.

---

## 4. Privacy & Safety Commitments

- **No Keylogging:** The agent never records keystrokes, clipboard buffers, or browser credentials.
- **No Private Document Collection:** Telemetry is strictly metadata-based (paths, PIDs, sizes, timestamps). File contents are never read or uploaded.
- **No Command Execution:** The agent does not expose any RPC or socket listener to execute commands received from the backend.
