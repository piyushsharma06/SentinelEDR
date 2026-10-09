"""Security event schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NormalizedEvent(BaseModel):
    event_uuid: str = Field(..., min_length=8, max_length=64)
    host_id: str = Field(..., min_length=4, max_length=64)
    event_type: str = Field(..., pattern="^(process_creation|network_connection|file_activity|agent_health)$")
    timestamp: datetime
    schema_version: str = Field(default="1.0")
    data: Dict[str, Any] = Field(..., description="Telemetry event payload")
    is_synthetic: bool = False


class EventIngestBatch(BaseModel):
    events: List[NormalizedEvent] = Field(..., min_length=1, max_length=500)


class EventIngestResponse(BaseModel):
    accepted: int
    rejected: int
    duplicates: int
    alerts_generated: int


class EventOut(BaseModel):
    id: int
    event_uuid: str
    host_id: str
    event_type: str
    timestamp: datetime
    ingested_at: datetime
    schema_version: str
    data: Dict[str, Any]
    process_name: Optional[str] = None
    process_id: Optional[int] = None
    parent_process_name: Optional[str] = None
    parent_process_id: Optional[int] = None
    command_line: Optional[str] = None
    username: Optional[str] = None
    network_remote_ip: Optional[str] = None
    network_remote_port: Optional[int] = None
    network_protocol: Optional[str] = None
    file_path: Optional[str] = None
    file_action: Optional[str] = None
    is_synthetic: bool

    model_config = {"from_attributes": True}
