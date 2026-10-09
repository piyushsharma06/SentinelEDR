"""Audit log database model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.database.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor_username = Column(String(64), index=True, nullable=False)
    action = Column(String(64), index=True, nullable=False)  # alert.update_status, incident.create, rule.toggle, auth.login, etc.
    resource_type = Column(String(64), index=True, nullable=False)  # alert, incident, host, rule, user, auth
    resource_id = Column(String(64), nullable=True, index=True)
    details = Column(JSON, default=dict, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)
    ip_address = Column(String(64), nullable=True)

    def __repr__(self) -> str:
        return f"<AuditLog(actor='{self.actor_username}', action='{self.action}', target='{self.resource_type}:{self.resource_id}')>"
