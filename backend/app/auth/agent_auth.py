"""Agent authentication mechanism separating agent telemetry credentials from analyst credentials."""

from typing import Optional
from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.agent_credential import AgentCredential
from app.models.host import Host
from app.auth.security import hash_api_key


def verify_agent_api_key(
    x_agent_key: Optional[str] = Header(None, alias="X-Agent-Key"),
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: Session = Depends(get_db)
) -> AgentCredential:
    """
    Authenticate an incoming agent telemetry payload using its dedicated agent API key.
    Rejects analyst JWTs or invalid/revoked agent keys.
    """
    raw_key = None
    if x_agent_key:
        raw_key = x_agent_key.strip()
    elif authorization and authorization.lower().startswith("bearer "):
        token_candidate = authorization.split(" ", 1)[1].strip()
        if token_candidate.startswith("sentinel_agent_"):
            raw_key = token_candidate

    if not raw_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Agent API key required (via X-Agent-Key header)",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    # Hash raw key and look up in database
    key_hash = hash_api_key(raw_key)
    credential = db.query(AgentCredential).filter(AgentCredential.api_key_hash == key_hash).first()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid agent API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    if not credential.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Agent API key has been revoked",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    return credential
