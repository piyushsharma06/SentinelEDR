"""Role-Based Access Control (RBAC) and authentication dependencies."""

from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.analyst import AnalystUser
from app.auth.security import decode_access_token

security_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    auth_header: HTTPAuthorizationCredentials = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> AnalystUser:
    """Extract and authenticate analyst user from Bearer JWT token."""
    if not auth_header or not auth_header.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = auth_header.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or malformed authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    username: str = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing subject identifier",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.query(AnalystUser).filter(AnalystUser.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user no longer exists",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Analyst account is deactivated"
        )

    return user


def require_roles(allowed_roles: List[str]):
    """Decorator/dependency enforcing that the authenticated user possesses one of the allowed roles."""
    def role_checker(current_user: AnalystUser = Depends(get_current_user)) -> AnalystUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of the following roles: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker


# Convenient role dependencies
get_current_active_user = Depends(get_current_user)
require_admin = require_roles(["admin"])
require_analyst_or_admin = require_roles(["admin", "analyst"])
require_any_authenticated = require_roles(["admin", "analyst", "viewer"])
