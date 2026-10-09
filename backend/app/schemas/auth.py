"""Authentication schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)


class AnalystOut(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: AnalystOut


class AnalystCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(default="analyst", pattern="^(admin|analyst|viewer)$")


class AgentEnrollmentRequest(BaseModel):
    host_id: str = Field(..., min_length=6, max_length=64)
    hostname: str = Field(..., min_length=1, max_length=255)
    os_platform: str = Field(default="Windows")
    os_version: Optional[str] = None
    agent_version: str = Field(default="1.0.0")
    enrollment_token: str = Field(..., min_length=8)


class AgentEnrollmentResponse(BaseModel):
    host_id: str
    api_key: str
    message: str
