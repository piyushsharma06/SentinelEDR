"""Host schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HostOut(BaseModel):
    id: int
    host_id: str
    hostname: str
    os_platform: str
    os_version: Optional[str] = None
    agent_version: str
    first_seen: datetime
    last_seen: datetime
    status: str
    ip_addresses: List[str]
    system_info: Dict[str, Any]
    is_synthetic: bool
    alerts_count: int = 0

    model_config = {"from_attributes": True}


class HostRegisterRequest(BaseModel):
    host_id: str = Field(..., min_length=6, max_length=64)
    hostname: str = Field(..., min_length=1, max_length=255)
    os_platform: str = Field(default="Windows")
    os_version: Optional[str] = None
    agent_version: str = Field(default="1.0.0")
    ip_addresses: List[str] = Field(default_factory=list)
    system_info: Dict[str, Any] = Field(default_factory=dict)
    is_synthetic: bool = False
