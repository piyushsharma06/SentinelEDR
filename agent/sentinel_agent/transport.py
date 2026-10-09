"""HTTP Transport layer for communicating with SentinelEDR backend API."""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple
import httpx
from sentinel_agent.config import AgentConfig

logger = logging.getLogger(__name__)


class AgentTransport:
    """Handles authenticated HTTP communication, enrollment, and event batch submission."""

    def __init__(self, config: AgentConfig, host_id: str):
        self.config = config
        self.host_id = host_id
        self.backend_url = config.backend_url.rstrip("/")
        self.api_key = config.agent_api_key
        self.client = httpx.Client(
            timeout=config.request_timeout_seconds,
            headers={"User-Agent": "SentinelEDR-Agent/1.0.0"}
        )

    def check_backend_health(self) -> bool:
        """Check if backend API server is reachable."""
        try:
            resp = self.client.get(f"{self.backend_url}/health")
            return resp.status_code == 200
        except Exception:
            return False

    def enroll(self, hostname: str, os_platform: str = "Windows") -> Optional[str]:
        """
        Enroll with the backend using the pre-shared enrollment token.
        Returns the issued agent API key.
        """
        if not self.config.enrollment_token:
            logger.error("Cannot auto-enroll: no enrollment token configured.")
            return None

        url = f"{self.backend_url}/api/v1/auth/enroll-agent"
        payload = {
            "host_id": self.host_id,
            "hostname": hostname,
            "os_platform": os_platform,
            "agent_version": "1.0.0",
            "enrollment_token": self.config.enrollment_token
        }

        try:
            resp = self.client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                key = data.get("api_key")
                self.api_key = key
                logger.info(f"Successfully enrolled agent with backend. Key prefix: {key[:12]}...")
                return key
            else:
                logger.error(f"Enrollment failed with HTTP {resp.status_code}: {resp.text}")
                return None
        except Exception as e:
            logger.error(f"Network error during enrollment: {e}")
            return None

    def send_events_batch(self, events: List[Dict[str, Any]]) -> Tuple[bool, int, str]:
        """
        Send a batch of events to backend.
        Returns: (success, accepted_count, error_message)
        """
        if not self.api_key:
            return False, 0, "No API key configured for agent."

        if not events:
            return True, 0, ""

        url = f"{self.backend_url}/api/v1/events"
        headers = {
            "X-Agent-Key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {"events": events}

        attempts = 0
        max_retries = self.config.max_retries
        backoff = self.config.backoff_factor_seconds

        while attempts < max_retries:
            attempts += 1
            try:
                resp = self.client.post(url, json=payload, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    accepted = data.get("accepted", len(events))
                    return True, accepted, ""
                elif resp.status_code == 401:
                    return False, 0, "Authentication error: Agent API key was rejected or revoked."
                else:
                    logger.warning(f"Batch submission attempt {attempts} failed: HTTP {resp.status_code} - {resp.text}")
            except httpx.RequestError as exc:
                logger.warning(f"Network error on attempt {attempts}: {exc}")

            if attempts < max_retries:
                time.sleep(backoff * attempts)

        return False, 0, f"Exceeded {max_retries} retry attempts."

    def close(self):
        self.client.close()
