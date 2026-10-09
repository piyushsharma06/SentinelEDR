"""Detection rule management service."""

from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.rule import DetectionRule
from app.services.audit_service import log_audit_event


def get_rules(
    db: Session,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    enabled: Optional[bool] = None
) -> List[DetectionRule]:
    """Retrieve all loaded detection rules."""
    query = db.query(DetectionRule)
    if severity:
        query = query.filter(DetectionRule.severity == severity.lower())
    if category:
        query = query.filter(DetectionRule.category == category)
    if enabled is not None:
        query = query.filter(DetectionRule.enabled == enabled)
    return query.order_by(DetectionRule.rule_id).all()


def get_rule_by_id(db: Session, rule_id: str) -> Optional[DetectionRule]:
    """Retrieve single detection rule."""
    if rule_id.isdigit():
        return db.query(DetectionRule).filter(DetectionRule.id == int(rule_id)).first()
    return db.query(DetectionRule).filter(DetectionRule.rule_id == rule_id).first()


def toggle_rule(
    db: Session,
    rule_id: str,
    enabled: bool,
    actor_username: str,
    ip_address: Optional[str] = None
) -> DetectionRule:
    """Enable or disable a detection rule."""
    rule = get_rule_by_id(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detection rule '{rule_id}' not found"
        )

    rule.enabled = enabled
    db.commit()
    db.refresh(rule)

    log_audit_event(
        db=db,
        actor_username=actor_username,
        action="rule.toggle",
        resource_type="rule",
        resource_id=rule.rule_id,
        details={"enabled": enabled},
        ip_address=ip_address
    )

    return rule
