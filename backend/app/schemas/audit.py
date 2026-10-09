"""Audit log schemas."""

from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel


class AuditLogOut(BaseModel):
    id: int
    actor_username: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: Dict[str, Any]
    timestamp: datetime
    ip_address: Optional[str] = None

    model_config = {"from_attributes": True}
