"""Authentication and agent enrollment router."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.config import settings
from app.database.session import get_db
from app.models.analyst import AnalystUser
from app.models.agent_credential import AgentCredential
from app.models.host import Host
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    AnalystOut,
    AgentEnrollmentRequest,
    AgentEnrollmentResponse
)
from app.auth.security import (
    verify_password,
    create_access_token,
    generate_agent_api_key
)
from app.auth.rbac import get_current_user
from app.services.audit_service import log_audit_event

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """Authenticate analyst user and generate a JWT access token."""
    user = db.query(AnalystUser).filter(AnalystUser.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analyst user account is inactive"
        )

    user.last_login = datetime.now(timezone.utc)
    db.commit()

    token = create_access_token(data={"sub": user.username, "role": user.role})

    log_audit_event(
        db=db,
        actor_username=user.username,
        action="auth.login",
        resource_type="auth",
        resource_id=str(user.id),
        details={"role": user.role},
        ip_address=request.client.host if request.client else None
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user=AnalystOut.model_validate(user)
    )


@router.get("/me", response_model=AnalystOut)
def get_current_user_profile(current_user: AnalystUser = Depends(get_current_user)):
    """Retrieve profile of the currently authenticated analyst."""
    return AnalystOut.model_validate(current_user)


@router.post("/enroll-agent", response_model=AgentEnrollmentResponse)
def enroll_agent(
    payload: AgentEnrollmentRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Enroll a new Windows endpoint agent using the pre-shared enrollment token.
    Generates and returns a dedicated per-agent API key.
    """
    if payload.enrollment_token != settings.agent_enrollment_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid agent enrollment token"
        )

    now_utc = datetime.now(timezone.utc)

    # Upsert Host
    host = db.query(Host).filter(Host.host_id == payload.host_id).first()
    if not host:
        host = Host(
            host_id=payload.host_id,
            hostname=payload.hostname,
            os_platform=payload.os_platform,
            os_version=payload.os_version,
            agent_version=payload.agent_version,
            first_seen=now_utc,
            last_seen=now_utc,
            status="online",
            is_synthetic=False
        )
        db.add(host)
    else:
        host.hostname = payload.hostname
        host.os_platform = payload.os_platform
        if payload.os_version:
            host.os_version = payload.os_version
        host.agent_version = payload.agent_version
        host.last_seen = now_utc
        host.status = "online"

    # Revoke old credentials for this host if any exist
    old_creds = db.query(AgentCredential).filter(AgentCredential.host_id == payload.host_id, AgentCredential.is_active == True).all()
    for c in old_creds:
        c.is_active = False
        c.revoked_at = now_utc

    # Generate new credential
    raw_key, key_hash, prefix = generate_agent_api_key()
    cred = AgentCredential(
        host_id=payload.host_id,
        api_key_hash=key_hash,
        api_key_prefix=prefix,
        is_active=True,
        created_at=now_utc,
        description=f"Auto-enrolled agent key for {payload.hostname}"
    )
    db.add(cred)
    db.commit()

    log_audit_event(
        db=db,
        actor_username=f"agent:{payload.host_id}",
        action="agent.enrolled",
        resource_type="agent_credential",
        resource_id=payload.host_id,
        details={"hostname": payload.hostname, "prefix": prefix},
        ip_address=request.client.host if request.client else None
    )

    return AgentEnrollmentResponse(
        host_id=payload.host_id,
        api_key=raw_key,
        message="Agent enrolled successfully. Store this API key securely."
    )
