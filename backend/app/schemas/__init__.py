"""Pydantic schemas initialization."""

from app.schemas.common import PaginationParams, PaginatedResponse
from app.schemas.auth import (
    LoginRequest,
    AnalystOut,
    TokenResponse,
    AnalystCreate,
    AgentEnrollmentRequest,
    AgentEnrollmentResponse
)
from app.schemas.host import HostOut, HostRegisterRequest
from app.schemas.event import NormalizedEvent, EventIngestBatch, EventIngestResponse, EventOut
from app.schemas.rule import DetectionRuleOut, RuleToggleRequest
from app.schemas.alert import AlertOut, AlertUpdate
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentOut
from app.schemas.audit import AuditLogOut
from app.schemas.stats import DashboardStatsOut

__all__ = [
    "PaginationParams",
    "PaginatedResponse",
    "LoginRequest",
    "AnalystOut",
    "TokenResponse",
    "AnalystCreate",
    "AgentEnrollmentRequest",
    "AgentEnrollmentResponse",
    "HostOut",
    "HostRegisterRequest",
    "NormalizedEvent",
    "EventIngestBatch",
    "EventIngestResponse",
    "EventOut",
    "DetectionRuleOut",
    "RuleToggleRequest",
    "AlertOut",
    "AlertUpdate",
    "IncidentCreate",
    "IncidentUpdate",
    "IncidentOut",
    "AuditLogOut",
    "DashboardStatsOut"
]
