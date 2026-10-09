"""Analyst user database model."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.database.session import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AnalystUser(Base):
    __tablename__ = "analysts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(32), default="analyst", nullable=False)  # admin, analyst, viewer
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self) -> str:
        return f"<AnalystUser(username='{self.username}', role='{self.role}')>"
