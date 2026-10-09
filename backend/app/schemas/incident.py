"""Incident schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.alert import AlertOut


class InvestigationNote(BaseModel):
    id: str
    author: str
    text: str
    timestamp: str


class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    severity: str = Field(default="medium", pattern="^(critical|high|medium|low|info)$")
    assigned_to: Optional[str] = None
    alert_ids: Optional[List[str]] = Field(default_factory=list)


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = Field(None, pattern="^(critical|high|medium|low|info)$")
    status: Optional[str] = Field(None, pattern="^(open|investigating|contained|resolved|closed)$")
    assigned_to: Optional[str] = None
    add_note: Optional[str] = None
    link_alert_ids: Optional[List[str]] = None
    unlink_alert_ids: Optional[List[str]] = None


class IncidentOut(BaseModel):
    id: int
    incident_id: str
    title: str
    description: str
    severity: str
    status: str
    assigned_to: Optional[str] = None
    investigation_notes: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    is_synthetic: bool
    alerts: Optional[List[AlertOut]] = None

    model_config = {"from_attributes": True}
