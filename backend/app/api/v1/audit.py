"""Audit Logs API router."""

import math
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.session import get_db
from app.models.analyst import AnalystUser
from app.models.audit_log import AuditLog
from app.schemas.common import PaginatedResponse
from app.schemas.audit import AuditLogOut
from app.auth.rbac import require_analyst_or_admin

router = APIRouter(prefix="/audit-logs", tags=["Audit"])


@router.get("", response_model=PaginatedResponse[AuditLogOut])
def list_audit_logs(
    actor: Optional[str] = Query(None, description="Filter by actor username"),
    action: Optional[str] = Query(None, description="Filter by action name"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: AnalystUser = Depends(require_analyst_or_admin)
):
    """Retrieve audit log entries for governance and compliance tracking."""
    query = db.query(AuditLog)
    if actor:
        query = query.filter(AuditLog.actor_username == actor)
    if action:
        query = query.filter(AuditLog.action == action)
    if resource_type:
        query = query.filter(AuditLog.resource_type == resource_type)

    total = query.count()
    items = query.order_by(desc(AuditLog.timestamp)).offset((page - 1) * page_size).limit(page_size).all()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    return PaginatedResponse[AuditLogOut](
        items=[AuditLogOut.model_validate(log) for log in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )
