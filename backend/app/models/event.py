"""Security event database model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# Association table for Alert <-> SecurityEvent many-to-many relationship
alert_events_association = Table(
    "alert_events",
    Base.metadata,
    Column("alert_id", Integer, ForeignKey("alerts.id", ondelete="CASCADE"), primary_key=True),
    Column("event_id", Integer, ForeignKey("events.id", ondelete="CASCADE"), primary_key=True)
)


class SecurityEvent(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    event_uuid = Column(String(64), unique=True, index=True, nullable=False)
    host_id = Column(String(64), ForeignKey("hosts.host_id", ondelete="CASCADE"), index=True, nullable=False)
    event_type = Column(String(64), index=True, nullable=False)  # process_creation, network_connection, file_activity, agent_health
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    ingested_at = Column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)
    schema_version = Column(String(16), default="1.0", nullable=False)
    data = Column(JSON, nullable=False)

    # Flattened metadata for high-efficiency indexed queries
    process_name = Column(String(255), index=True, nullable=True)
    process_id = Column(Integer, nullable=True)
    parent_process_name = Column(String(255), index=True, nullable=True)
    parent_process_id = Column(Integer, nullable=True)
    command_line = Column(Text, nullable=True)
    username = Column(String(128), index=True, nullable=True)
    network_remote_ip = Column(String(64), index=True, nullable=True)
    network_remote_port = Column(Integer, nullable=True)
    network_protocol = Column(String(16), nullable=True)
    file_path = Column(Text, nullable=True)
    file_action = Column(String(32), nullable=True)
    is_synthetic = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    host = relationship("Host", back_populates="events")
    alerts = relationship("Alert", secondary=alert_events_association, back_populates="events")

    def __repr__(self) -> str:
        return f"<SecurityEvent(uuid='{self.event_uuid}', type='{self.event_type}', host='{self.host_id}')>"
