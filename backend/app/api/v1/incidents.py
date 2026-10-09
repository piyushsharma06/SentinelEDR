"""Incidents API router."""

import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.analyst import AnalystUser
from app.schemas.common import PaginatedResponse
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentOut
from app.services.incident_service import (
    get_incidents,
    get_incident_by_id,
    create_incident,
    update_incident
)
from app.auth.rbac import require_any_authenticated, require_analyst_or_admin

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("", response_model=PaginatedResponse[IncidentOut])
def list_incidents(
    status: Optional[str] = Query(None, description="Filter by status (open, investigating, contained, resolved, closed)"),
    severity: Optional[str] = Query(None, description="Filter by severity (critical, high, medium, low, info)"),
    assigned_to: Optional[str] = Query(None, description="Filter by assigned analyst"),
    is_synthetic: Optional[bool] = Query(None, description="Filter demo synthetic incidents"),
    search: Optional[str] = Query(None, description="Search title, description, or ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: AnalystUser = Depends(require_any_authenticated)
):
    """List security incidents with pagination and filtering."""
    items, total = get_incidents(
        db,
        status=status,
        severity=severity,
        assigned_to=assigned_to,
        is_synthetic=is_synthetic,
        search=search,
        page=page,
        page_size=page_size
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return PaginatedResponse[IncidentOut](
        items=[IncidentOut.model_validate(inc) for inc in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.post("", response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
def create_new_incident(
    payload: IncidentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AnalystUser = Depends(require_analyst_or_admin)
):
    """Create a new security incident and link initial alerts."""
    incident = create_incident(
        db=db,
        create_data=payload,
        actor_username=current_user.username,
        ip_address=request.client.host if request.client else None
    )
    return IncidentOut.model_validate(incident)


@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(
    incident_id: str,
    db: Session = Depends(get_db),
    current_user: AnalystUser = Depends(require_any_authenticated)
):
    """Retrieve full details for an incident, including linked alerts and timeline notes."""
    inc = get_incident_by_id(db, incident_id)
    if not inc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found"
        )
    return IncidentOut.model_validate(inc)


@router.patch("/{incident_id}", response_model=IncidentOut)
def patch_incident(
    incident_id: str,
    payload: IncidentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AnalystUser = Depends(require_analyst_or_admin)
):
    """Update incident status, severity, assignment, add investigation notes, or link/unlink alerts."""
    updated = update_incident(
        db=db,
        incident_id=incident_id,
        update_data=payload,
        actor_username=current_user.username,
        ip_address=request.client.host if request.client else None
    )
    return IncidentOut.model_validate(updated)
