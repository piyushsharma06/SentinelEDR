"""Alerts API router."""

import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.analyst import AnalystUser
from app.schemas.common import PaginatedResponse
from app.schemas.alert import AlertOut, AlertUpdate
from app.services.alert_service import get_alerts, get_alert_by_id, update_alert
from app.auth.rbac import require_any_authenticated, require_analyst_or_admin

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=PaginatedResponse[AlertOut])
def list_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity (critical, high, medium, low, info)"),
    status: Optional[str] = Query(None, description="Filter by status (new, acknowledged, investigating, resolved, false_positive)"),
    host_id: Optional[str] = Query(None, description="Filter by host ID"),
    rule_id: Optional[str] = Query(None, description="Filter by detection rule ID"),
    incident_id: Optional[str] = Query(None, description="Filter by linked incident ID"),
    is_synthetic: Optional[bool] = Query(None, description="Filter demo synthetic alerts"),
    search: Optional[str] = Query(None, description="Search across title, description, or host"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: AnalystUser = Depends(require_any_authenticated)
):
    """List detection alerts with pagination and filtering."""
    items, total = get_alerts(
        db,
        severity=severity,
        status=status,
        host_id=host_id,
        rule_id=rule_id,
        incident_id=incident_id,
        is_synthetic=is_synthetic,
        search=search,
        page=page,
        page_size=page_size
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return PaginatedResponse[AlertOut](
        items=[AlertOut.model_validate(alt) for alt in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(
    alert_id: str,
    db: Session = Depends(get_db),
    current_user: AnalystUser = Depends(require_any_authenticated)
):
    """Retrieve full details for an alert, including evidence and linked events."""
    alt = get_alert_by_id(db, alert_id)
    if not alt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert '{alert_id}' not found"
        )
    return AlertOut.model_validate(alt)


@router.patch("/{alert_id}", response_model=AlertOut)
def patch_alert(
    alert_id: str,
    update_data: AlertUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AnalystUser = Depends(require_analyst_or_admin)
):
    """Update alert triage status, assignment, false positive reason, or link to an incident."""
    updated = update_alert(
        db=db,
        alert_id=alert_id,
        update_data=update_data,
        actor_username=current_user.username,
        ip_address=request.client.host if request.client else None
    )
    return AlertOut.model_validate(updated)
