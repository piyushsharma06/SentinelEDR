"""Incident management and investigation workflow service."""

import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
from app.models.incident import Incident
from app.models.alert import Alert
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.services.audit_service import log_audit_event

VALID_INCIDENT_STATUSES = {"open", "investigating", "contained", "resolved", "closed"}


def get_incidents(
    db: Session,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    assigned_to: Optional[str] = None,
    is_synthetic: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
) -> Tuple[List[Incident], int]:
    """Retrieve filtered, paginated incidents."""
    query = db.query(Incident)

    if status:
        query = query.filter(Incident.status == status.lower())
    if severity:
        query = query.filter(Incident.severity == severity.lower())
    if assigned_to:
        query = query.filter(Incident.assigned_to == assigned_to)
    if is_synthetic is not None:
        query = query.filter(Incident.is_synthetic == is_synthetic)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (Incident.title.ilike(search_fmt)) |
            (Incident.description.ilike(search_fmt)) |
            (Incident.incident_id.ilike(search_fmt))
        )

    total = query.count()
    incidents = (
        query.order_by(desc(Incident.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return incidents, total


def get_incident_by_id(db: Session, incident_id: str) -> Optional[Incident]:
    """Retrieve single incident with associated alerts."""
    if incident_id.isdigit():
        return db.query(Incident).filter(Incident.id == int(incident_id)).first()
    return db.query(Incident).filter(Incident.incident_id == incident_id).first()


def create_incident(
    db: Session,
    create_data: IncidentCreate,
    actor_username: str,
    ip_address: Optional[str] = None,
    is_synthetic: bool = False
) -> Incident:
    """Create a new security incident and link initial alerts."""
    inc_uid = f"INC-{uuid.uuid4().hex[:8].upper()}"
    now_utc = datetime.now(timezone.utc)

    # If any alert is synthetic, mark incident as synthetic
    if create_data.alert_ids:
        synthetic_alerts_count = (
            db.query(Alert)
            .filter(Alert.alert_id.in_(create_data.alert_ids), Alert.is_synthetic == True)
            .count()
        )
        if synthetic_alerts_count > 0:
            is_synthetic = True

    incident = Incident(
        incident_id=inc_uid,
        title=create_data.title,
        description=create_data.description,
        severity=create_data.severity,
        status="open",
        assigned_to=create_data.assigned_to or actor_username,
        investigation_notes=[{
            "id": uuid.uuid4().hex[:8],
            "author": actor_username,
            "text": f"Incident created with severity {create_data.severity.upper()}.",
            "timestamp": now_utc.isoformat()
        }],
        created_at=now_utc,
        updated_at=now_utc,
        is_synthetic=is_synthetic
    )
    db.add(incident)
    db.flush()

    # Link initial alerts
    if create_data.alert_ids:
        alerts = db.query(Alert).filter(Alert.alert_id.in_(create_data.alert_ids)).all()
        for alt in alerts:
            alt.incident_id = incident.incident_id
            if alt.status in ["new", "acknowledged"]:
                alt.status = "investigating"

    db.commit()
    db.refresh(incident)

    log_audit_event(
        db=db,
        actor_username=actor_username,
        action="incident.create",
        resource_type="incident",
        resource_id=incident.incident_id,
        details={
            "title": incident.title,
            "severity": incident.severity,
            "linked_alerts": create_data.alert_ids or []
        },
        ip_address=ip_address
    )

    return incident


def update_incident(
    db: Session,
    incident_id: str,
    update_data: IncidentUpdate,
    actor_username: str,
    ip_address: Optional[str] = None
) -> Incident:
    """Update incident attributes, add investigation notes, or link/unlink alerts."""
    incident = get_incident_by_id(db, incident_id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident '{incident_id}' not found"
        )

    changes = {}
    now_utc = datetime.now(timezone.utc)

    if update_data.title and update_data.title != incident.title:
        changes["title"] = {"from": incident.title, "to": update_data.title}
        incident.title = update_data.title

    if update_data.description and update_data.description != incident.description:
        changes["description"] = "updated"
        incident.description = update_data.description

    if update_data.severity and update_data.severity != incident.severity:
        changes["severity"] = {"from": incident.severity, "to": update_data.severity}
        incident.severity = update_data.severity

    if update_data.status and update_data.status != incident.status:
        if update_data.status not in VALID_INCIDENT_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid incident status: {update_data.status}"
            )
        changes["status"] = {"from": incident.status, "to": update_data.status}
        incident.status = update_data.status

    if update_data.assigned_to is not None and update_data.assigned_to != incident.assigned_to:
        changes["assigned_to"] = {"from": incident.assigned_to, "to": update_data.assigned_to}
        incident.assigned_to = update_data.assigned_to

    if update_data.add_note:
        notes = list(incident.investigation_notes or [])
        notes.append({
            "id": uuid.uuid4().hex[:8],
            "author": actor_username,
            "text": update_data.add_note,
            "timestamp": now_utc.isoformat()
        })
        incident.investigation_notes = notes
        changes["note_added"] = True

    if update_data.link_alert_ids:
        alerts = db.query(Alert).filter(Alert.alert_id.in_(update_data.link_alert_ids)).all()
        for alt in alerts:
            alt.incident_id = incident.incident_id
            if alt.status in ["new", "acknowledged"]:
                alt.status = "investigating"
        changes["linked_alerts"] = update_data.link_alert_ids

    if update_data.unlink_alert_ids:
        alerts = db.query(Alert).filter(Alert.alert_id.in_(update_data.unlink_alert_ids)).all()
        for alt in alerts:
            if alt.incident_id == incident.incident_id:
                alt.incident_id = None
        changes["unlinked_alerts"] = update_data.unlink_alert_ids

    incident.updated_at = now_utc
    db.commit()
    db.refresh(incident)

    if changes:
        log_audit_event(
            db=db,
            actor_username=actor_username,
            action="incident.update",
            resource_type="incident",
            resource_id=incident.incident_id,
            details=changes,
            ip_address=ip_address
        )

    return incident
