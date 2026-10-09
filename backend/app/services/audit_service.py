"""Audit service for recording analyst and system actions."""

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def log_audit_event(
    db: Session,
    actor_username: str,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """Create and persist an audit log entry."""
    entry = AuditLog(
        actor_username=actor_username,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        ip_address=ip_address
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
