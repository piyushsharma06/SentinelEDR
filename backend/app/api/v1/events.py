"""Events API router."""

import math
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.config import settings
from app.database.session import get_db
from app.models.analyst import AnalystUser
from app.models.agent_credential import AgentCredential
from app.schemas.common import PaginatedResponse
from app.schemas.event import EventIngestBatch, EventIngestResponse, EventOut
from app.services.event_service import ingest_events_batch, get_events, get_event_by_id
from app.auth.security import hash_api_key, decode_access_token
from app.auth.rbac import require_any_authenticated

router = APIRouter(prefix="/events", tags=["Events"])


def authenticate_agent_or_analyst(
    x_agent_key: Optional[str] = Header(None, alias="X-Agent-Key"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
):
    """
    Authenticate event ingestion: accepts valid active Agent API key OR analyst JWT.
    """
    # 1. Try Agent API Key
    raw_key = None
    if x_agent_key:
        raw_key = x_agent_key.strip()
    elif authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        if token.startswith("sentinel_agent_"):
            raw_key = token
        else:
            # 2. Try Analyst JWT Token
            payload = decode_access_token(token)
            if payload and "sub" in payload:
                user = db.query(AnalystUser).filter(AnalystUser.username == payload["sub"]).first()
                if user and user.is_active:
                    return {"type": "analyst", "identity": user.username}

    if raw_key:
        key_hash = hash_api_key(raw_key)
        cred = db.query(AgentCredential).filter(AgentCredential.api_key_hash == key_hash).first()
        if cred and cred.is_active:
            return {"type": "agent", "identity": cred.host_id}
        elif cred and not cred.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Agent API key has been revoked"
            )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Valid agent API key or analyst authentication required"
    )


@router.post("", response_model=EventIngestResponse)
def ingest_events(
    batch: EventIngestBatch,
    auth_ctx: dict = Depends(authenticate_agent_or_analyst),
    db: Session = Depends(get_db)
):
    """
    Ingest a batch of normalized security events from an enrolled agent or synthetic generator.
    Enforces batch limits and schema validation.
    """
    if len(batch.events) > settings.event_ingestion_batch_limit:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE if hasattr(status, "HTTP_413_CONTENT_TOO_LARGE") else 413,
            detail=f"Batch size {len(batch.events)} exceeds limit of {settings.event_ingestion_batch_limit}"
        )

    # If authenticated via agent key, verify event host_ids match the key's host_id
    if auth_ctx["type"] == "agent":
        key_host_id = auth_ctx["identity"]
        for ev in batch.events:
            if ev.host_id != key_host_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Agent credential for '{key_host_id}' cannot submit events for host '{ev.host_id}'"
                )

    accepted, rejected, duplicates, alerts_gen = ingest_events_batch(db, batch.events)

    return EventIngestResponse(
        accepted=accepted,
        rejected=rejected,
        duplicates=duplicates,
        alerts_generated=alerts_gen
    )


@router.get("", response_model=PaginatedResponse[EventOut])
def list_events(
    host_id: Optional[str] = Query(None, description="Filter by host ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    process_name: Optional[str] = Query(None, description="Filter by process name"),
    start_time: Optional[datetime] = Query(None, description="UTC start time"),
    end_time: Optional[datetime] = Query(None, description="UTC end time"),
    is_synthetic: Optional[bool] = Query(None, description="Filter demo synthetic events"),
    search: Optional[str] = Query(None, description="Search across command line, paths, and IPs"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: AnalystUser = Depends(require_any_authenticated)
):
    """Retrieve paginated security events for exploration."""
    items, total = get_events(
        db,
        host_id=host_id,
        event_type=event_type,
        process_name=process_name,
        start_time=start_time,
        end_time=end_time,
        is_synthetic=is_synthetic,
        search=search,
        page=page,
        page_size=page_size
    )
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    return PaginatedResponse[EventOut](
        items=[EventOut.model_validate(ev) for ev in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{event_id}", response_model=EventOut)
def get_event(
    event_id: str,
    db: Session = Depends(get_db),
    current_user: AnalystUser = Depends(require_any_authenticated)
):
    """Retrieve full details for an individual event."""
    ev = get_event_by_id(db, event_id)
    if not ev:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Security event '{event_id}' not found"
        )
    return EventOut.model_validate(ev)
