"""Detection Rules API router."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.analyst import AnalystUser
from app.schemas.rule import DetectionRuleOut, RuleToggleRequest
from app.services.rule_service import get_rules, get_rule_by_id, toggle_rule
from app.auth.rbac import require_any_authenticated, require_admin

router = APIRouter(prefix="/rules", tags=["Detection Rules"])


@router.get("", response_model=List[DetectionRuleOut])
def list_detection_rules(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    category: Optional[str] = Query(None, description="Filter by category"),
    enabled: Optional[bool] = Query(None, description="Filter by enabled state"),
    db: Session = Depends(get_db),
    current_user: AnalystUser = Depends(require_any_authenticated)
):
    """List loaded YAML-based detection rules."""
    rules = get_rules(db, severity=severity, category=category, enabled=enabled)
    return [DetectionRuleOut.model_validate(r) for r in rules]


@router.get("/{rule_id}", response_model=DetectionRuleOut)
def get_detection_rule(
    rule_id: str,
    db: Session = Depends(get_db),
    current_user: AnalystUser = Depends(require_any_authenticated)
):
    """Retrieve details, logic, and MITRE mapping for a single detection rule."""
    rule = get_rule_by_id(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Detection rule '{rule_id}' not found"
        )
    return DetectionRuleOut.model_validate(rule)


@router.patch("/{rule_id}/toggle", response_model=DetectionRuleOut)
def toggle_detection_rule(
    rule_id: str,
    payload: RuleToggleRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: AnalystUser = Depends(require_admin)
):
    """Enable or disable a detection rule (Administrator only)."""
    updated = toggle_rule(
        db=db,
        rule_id=rule_id,
        enabled=payload.enabled,
        actor_username=current_user.username,
        ip_address=request.client.host if request.client else None
    )
    return DetectionRuleOut.model_validate(updated)
