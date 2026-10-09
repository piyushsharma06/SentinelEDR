"""Alert schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.event import EventOut


class AlertOut(BaseModel):
    id: int
    alert_id: str
    rule_id: str
    host_id: str
    severity: str
    status: str
    title: str
    description: str
    evidence_summary: Dict[str, Any]
    mitre_technique_id: Optional[str] = None
    mitre_technique_name: Optional[str] = None
    mitre_tactic: Optional[str] = None
    first_seen: datetime
    last_seen: datetime
    event_count: int
    assigned_to: Optional[str] = None
    incident_id: Optional[str] = None
    false_positive_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_synthetic: bool
    events: Optional[List[EventOut]] = None

    model_config = {"from_attributes": True}


class AlertUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(new|acknowledged|investigating|resolved|false_positive)$")
    assigned_to: Optional[str] = None
    incident_id: Optional[str] = None
    false_positive_reason: Optional[str] = None
