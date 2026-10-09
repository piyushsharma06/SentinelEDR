"""Agent configuration parser and validator."""

import os
from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel, Field, field_validator


class AgentConfig(BaseModel):
    backend_url: str = Field(default="http://127.0.0.1:8000")
    agent_api_key: Optional[str] = Field(default=None)
    enrollment_token: Optional[str] = Field(default="sentinel-agent-enrollment-secret-key-change-me")
    auto_enroll: bool = Field(default=True)

    process_poll_interval: int = Field(default=5, ge=1, le=60)
    network_poll_interval: int = Field(default=10, ge=1, le=120)
    health_interval: int = Field(default=30, ge=5, le=300)

    batch_size: int = Field(default=50, ge=1, le=100)
    flush_interval_seconds: int = Field(default=5, ge=1, le=60)
    request_timeout_seconds: int = Field(default=10, ge=2, le=30)
    max_retries: int = Field(default=3, ge=1, le=10)
    backoff_factor_seconds: int = Field(default=2, ge=1, le=10)

    queue_db_path: str = Field(default="agent_queue.db")
    max_queue_items: int = Field(default=2000, ge=100, le=10000)

    file_monitoring_enabled: bool = Field(default=False)
    monitored_directory: str = Field(default="./monitored_test_dir")

    log_level: str = Field(default="INFO")
    log_file: Optional[str] = Field(default="agent.log")

    @field_validator("monitored_directory")
    @classmethod
    def validate_safe_directory(cls, v: str) -> str:
        """Enforce safety: never allow monitoring critical system or root paths."""
        p = Path(v).resolve()
        disallowed_roots = ["c:\\", "c:\\windows", "c:\\program files", "/", "/etc", "/usr", "/root"]
        p_str = str(p).lower().rstrip("\\/")
        for disallowed in disallowed_roots:
            if p_str == disallowed.lower().rstrip("\\/"):
                raise ValueError(f"File monitoring cannot target root or system directory: {v}")
        return v


def load_agent_config(config_file: Optional[str] = None) -> AgentConfig:
    """Load configuration from YAML file and override with environment variables."""
    raw_dict = {}

    # Check candidates for config file
    candidates = [config_file, "agent/config.yaml", "config.yaml", "agent/config.example.yaml"]
    chosen_path = None
    for cand in candidates:
        if cand and os.path.exists(cand):
            chosen_path = cand
            break

    if chosen_path:
        with open(chosen_path, "r", encoding="utf-8") as f:
            raw_dict = yaml.safe_load(f) or {}

    # Override with environment variables
    if os.getenv("SENTINEL_BACKEND_URL"):
        raw_dict["backend_url"] = os.getenv("SENTINEL_BACKEND_URL")
    if os.getenv("SENTINEL_AGENT_API_KEY"):
        raw_dict["agent_api_key"] = os.getenv("SENTINEL_AGENT_API_KEY")
    if os.getenv("SENTINEL_ENROLLMENT_TOKEN"):
        raw_dict["enrollment_token"] = os.getenv("SENTINEL_ENROLLMENT_TOKEN")
    if os.getenv("SENTINEL_LOG_LEVEL"):
        raw_dict["log_level"] = os.getenv("SENTINEL_LOG_LEVEL")

    return AgentConfig(**raw_dict)
