"""Hosts API router."""

import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.analyst import AnalystUser
from app.schemas.common import PaginatedResponse
from app.schemas.host import HostOut
from app.services.host_service import get_hosts, get_host_by_id
from app.auth.rbac import require_any_authenticated

router = APIRouter(prefix="/hosts", tags=["Endpoints"])


@router.get("", response_model=PaginatedResponse[HostOut])
def list_hosts(
    status: Optional[str] = Query(None, description="Filter by status (online, offline, degraded, stale)"),
    search: Optional[str] = Query(None, description="Search hostname or host ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: AnalystUser = Depends(require_any_authenticated)
):
    """List enrolled endpoint hosts with pagination and filtering."""
    items, total = get_hosts(db, status_filter=status, search=search, page=page, page_size=page_size)
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return PaginatedResponse[HostOut](
        items=[HostOut(**h) for h in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{host_id}", response_model=HostOut)
def get_host(
    host_id: str,
    db: Session = Depends(get_db),
    current_user: AnalystUser = Depends(require_any_authenticated)
):
    """Retrieve details for a single host."""
    host_data = get_host_by_id(db, host_id)
    if not host_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Host '{host_id}' not found"
        )
    return HostOut(**host_data)
