"""Detection rule schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DetectionRuleOut(BaseModel):
    id: int
    rule_id: str
    name: str
    description: str
    severity: str
    category: str
    enabled: bool
    conditions: Dict[str, Any]
    mitre_technique_id: Optional[str] = None
    mitre_technique_name: Optional[str] = None
    mitre_tactic: Optional[str] = None
    version: str
    rationale: Optional[str] = None
    evidence_fields: List[str]
    false_positive_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RuleToggleRequest(BaseModel):
    enabled: bool
