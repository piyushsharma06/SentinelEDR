"""Host database model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Host(Base):
    __tablename__ = "hosts"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(String(64), unique=True, index=True, nullable=False)
    hostname = Column(String(255), index=True, nullable=False)
    os_platform = Column(String(64), nullable=False, default="Windows")
    os_version = Column(String(128), nullable=True)
    agent_version = Column(String(64), nullable=False, default="1.0.0")
    first_seen = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_seen = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, index=True, nullable=False)
    status = Column(String(32), default="online", index=True, nullable=False)  # online, offline, degraded, stale
    ip_addresses = Column(JSON, default=list, nullable=False)
    system_info = Column(JSON, default=dict, nullable=False)
    is_synthetic = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    events = relationship("SecurityEvent", back_populates="host", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="host", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Host(host_id='{self.host_id}', hostname='{self.hostname}', status='{self.status}')>"
