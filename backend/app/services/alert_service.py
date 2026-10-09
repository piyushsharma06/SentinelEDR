"""Alert service for alert triage, investigation, and lifecycle management."""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status
from app.models.alert import Alert
from app.models.incident import Incident
from app.schemas.alert import AlertUpdate
from app.services.audit_service import log_audit_event

VALID_ALERT_STATUSES = {"new", "acknowledged", "investigating", "resolved", "false_positive"}


def get_alerts(
    db: Session,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    host_id: Optional[str] = None,
    rule_id: Optional[str] = None,
    incident_id: Optional[str] = None,
    is_synthetic: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 50
) -> Tuple[List[Alert], int]:
    """Retrieve filtered, paginated alerts."""
    query = db.query(Alert)

    if severity:
        query = query.filter(Alert.severity == severity.lower())
    if status:
        query = query.filter(Alert.status == status.lower())
    if host_id:
        query = query.filter(Alert.host_id == host_id)
    if rule_id:
        query = query.filter(Alert.rule_id == rule_id)
    if incident_id:
        query = query.filter(Alert.incident_id == incident_id)
    if is_synthetic is not None:
        query = query.filter(Alert.is_synthetic == is_synthetic)
    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            (Alert.title.ilike(search_fmt)) |
            (Alert.description.ilike(search_fmt)) |
            (Alert.host_id.ilike(search_fmt)) |
            (Alert.alert_id.ilike(search_fmt))
        )

    total = query.count()
    alerts = (
        query.order_by(desc(Alert.last_seen))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return alerts, total


def get_alert_by_id(db: Session, alert_id: str) -> Optional[Alert]:
    """Retrieve single alert with linked events."""
    if alert_id.isdigit():
        return db.query(Alert).filter(Alert.id == int(alert_id)).first()
    return db.query(Alert).filter(Alert.alert_id == alert_id).first()


def update_alert(
    db: Session,
    alert_id: str,
    update_data: AlertUpdate,
    actor_username: str,
    ip_address: Optional[str] = None
) -> Alert:
    """Update alert status, assignment, false positive reason, or incident link."""
    alert = get_alert_by_id(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert '{alert_id}' not found"
        )

    changes = {}

    if update_data.status and update_data.status != alert.status:
        if update_data.status not in VALID_ALERT_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid alert status: {update_data.status}"
            )
        old_status = alert.status
        alert.status = update_data.status
        changes["status"] = {"from": old_status, "to": update_data.status}

    if update_data.assigned_to is not None and update_data.assigned_to != alert.assigned_to:
        old_assigned = alert.assigned_to
        alert.assigned_to = update_data.assigned_to
        changes["assigned_to"] = {"from": old_assigned, "to": update_data.assigned_to}

    if update_data.false_positive_reason is not None:
        alert.false_positive_reason = update_data.false_positive_reason
        changes["false_positive_reason"] = update_data.false_positive_reason

    if update_data.incident_id is not None:
        if update_data.incident_id != "":
            # Validate incident exists
            inc = db.query(Incident).filter(Incident.incident_id == update_data.incident_id).first()
            if not inc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Target incident '{update_data.incident_id}' does not exist"
                )
            alert.incident_id = update_data.incident_id
            changes["incident_id"] = update_data.incident_id
        else:
            alert.incident_id = None
            changes["incident_id"] = None

    if changes:
        alert.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(alert)

        log_audit_event(
            db=db,
            actor_username=actor_username,
            action="alert.update",
            resource_type="alert",
            resource_id=alert.alert_id,
            details=changes,
            ip_address=ip_address
        )

    return alert
