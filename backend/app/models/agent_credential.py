"""Agent credential database model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.database.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AgentCredential(Base):
    __tablename__ = "agent_credentials"

    id = Column(Integer, primary_key=True, index=True)
    host_id = Column(String(64), index=True, nullable=False)
    api_key_hash = Column(String(255), unique=True, index=True, nullable=False)
    api_key_prefix = Column(String(16), nullable=False)  # First few chars for identification in logs/UI
    is_active = Column(Boolean, default=True, index=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    description = Column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"<AgentCredential(host_id='{self.host_id}', prefix='{self.api_key_prefix}', active={self.is_active})>"
