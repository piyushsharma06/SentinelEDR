"""Configuration settings for SentinelEDR Backend using pydantic-settings."""

import os
from typing import List, Union
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    app_name: str = "SentinelEDR"
    app_version: str = "1.0.0"
    app_env: str = Field(default="development")
    debug: bool = Field(default=True)
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)

    # Database
    database_url: str = Field(default="sqlite:///./sentinel.db")

    # Security & Auth
    jwt_secret_key: str = Field(default="sentinel-insecure-default-change-in-production-32-bytes")
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=120)

    # Bootstrap Admin
    bootstrap_admin_username: str = Field(default="admin")
    bootstrap_admin_password: str = Field(default="SentinelAdmin!2026Secure")
    bootstrap_admin_role: str = Field(default="admin")

    # Agent Enrollment
    agent_enrollment_token: str = Field(default="sentinel-agent-enrollment-secret-key-change-me")

    # CORS
    cors_origins: Union[str, List[str]] = Field(
        default="http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    )

    # Detection & Rules
    rules_dir: str = Field(default="./rules")
    alert_deduplication_window_minutes: int = Field(default=10)
    event_ingestion_batch_limit: int = Field(default=100)
    login_rate_limit_per_minute: int = Field(default=15)
    demo_mode: bool = Field(default=True)

    @field_validator("cors_origins", mode="after")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


settings = Settings()
