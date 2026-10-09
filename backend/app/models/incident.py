"""Incident database model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(32), default="medium", index=True, nullable=False)  # critical, high, medium, low, info
    status = Column(String(32), default="open", index=True, nullable=False)  # open, investigating, contained, resolved, closed
    assigned_to = Column(String(128), nullable=True, index=True)
    investigation_notes = Column(JSON, default=list, nullable=False)  # list of note objects: [{"id": str, "author": str, "text": str, "timestamp": str}]
    created_at = Column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    is_synthetic = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    alerts = relationship("Alert", back_populates="incident")

    def __repr__(self) -> str:
        return f"<Incident(incident_id='{self.incident_id}', title='{self.title}', status='{self.status}')>"
