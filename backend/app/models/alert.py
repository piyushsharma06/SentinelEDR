"""Alert database model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base
from app.models.event import alert_events_association


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(String(64), unique=True, index=True, nullable=False)
    rule_id = Column(String(64), ForeignKey("rules.rule_id", ondelete="RESTRICT"), index=True, nullable=False)
    host_id = Column(String(64), ForeignKey("hosts.host_id", ondelete="CASCADE"), index=True, nullable=False)
    severity = Column(String(32), index=True, nullable=False)  # critical, high, medium, low, info
    status = Column(String(32), default="new", index=True, nullable=False)  # new, acknowledged, investigating, resolved, false_positive
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    evidence_summary = Column(JSON, nullable=False)
    mitre_technique_id = Column(String(32), index=True, nullable=True)
    mitre_technique_name = Column(String(255), nullable=True)
    mitre_tactic = Column(String(64), nullable=True)
    first_seen = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_seen = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, index=True, nullable=False)
    event_count = Column(Integer, default=1, nullable=False)
    assigned_to = Column(String(128), nullable=True, index=True)
    incident_id = Column(String(64), ForeignKey("incidents.incident_id", ondelete="SET NULL"), nullable=True, index=True)
    false_positive_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    is_synthetic = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    rule = relationship("DetectionRule", back_populates="alerts")
    host = relationship("Host", back_populates="alerts")
    events = relationship("SecurityEvent", secondary=alert_events_association, back_populates="alerts")
    incident = relationship("Incident", back_populates="alerts")

    def __repr__(self) -> str:
        return f"<Alert(alert_id='{self.alert_id}', rule_id='{self.rule_id}', status='{self.status}')>"
