"""Detection rule data models for YAML rule parsing and validation."""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class ConditionSchema(BaseModel):
    field: str = Field(..., description="Target event field or data path (e.g., process_name, command_line, file_path)")
    operator: Literal[
        "equals",
        "not_equals",
        "in",
        "not_in",
        "contains",
        "matches_any_substring",
        "matches_regex",
        "greater_than",
        "less_than",
        "not_in_cidr_or_local"
    ] = Field(..., description="Evaluation operator")
    value: Union[str, int, float, bool, List[Union[str, int, float]]] = Field(..., description="Value to test against")


class DetectionBlockSchema(BaseModel):
    event_type: str = Field(..., description="Target event type (e.g. process_creation, network_connection, file_activity, agent_health)")
    logic: Literal["all", "any"] = Field(default="all", description="Combining logic for conditions")
    conditions: List[ConditionSchema] = Field(default_factory=list)


class MitreAttackSchema(BaseModel):
    technique_id: str
    technique_name: str
    tactic: str


class RuleDefinitionSchema(BaseModel):
    id: str = Field(..., min_length=4, max_length=64, description="Unique rule identifier")
    name: str = Field(..., min_length=3, max_length=255)
    description: str
    severity: Literal["critical", "high", "medium", "low", "info"] = "medium"
    category: str = "General"
    enabled: bool = True
    version: str = "1.0.0"
    mitre_attack: Optional[MitreAttackSchema] = None
    detection: DetectionBlockSchema
    rationale: Optional[str] = None
    evidence_fields: List[str] = Field(default_factory=list)
    false_positive_notes: Optional[str] = None
