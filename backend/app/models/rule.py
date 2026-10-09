"""Detection rule database model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DetectionRule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(32), index=True, nullable=False)  # critical, high, medium, low, info
    category = Column(String(64), index=True, nullable=False)
    enabled = Column(Boolean, default=True, index=True, nullable=False)
    conditions = Column(JSON, nullable=False)  # Parsed YAML rule logic
    mitre_technique_id = Column(String(32), index=True, nullable=True)
    mitre_technique_name = Column(String(255), nullable=True)
    mitre_tactic = Column(String(64), nullable=True)
    version = Column(String(32), default="1.0.0", nullable=False)
    rationale = Column(Text, nullable=True)
    evidence_fields = Column(JSON, default=list, nullable=False)
    false_positive_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    alerts = relationship("Alert", back_populates="rule")

    def __repr__(self) -> str:
        return f"<DetectionRule(rule_id='{self.rule_id}', name='{self.name}', severity='{self.severity}')>"
