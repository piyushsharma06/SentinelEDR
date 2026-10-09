"""Authentication and authorization package."""

from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    generate_agent_api_key,
    hash_api_key
)
from app.auth.rbac import (
    get_current_user,
    require_roles,
    require_admin,
    require_analyst_or_admin,
    require_any_authenticated
)
from app.auth.agent_auth import verify_agent_api_key

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "generate_agent_api_key",
    "hash_api_key",
    "get_current_user",
    "require_roles",
    "require_admin",
    "require_analyst_or_admin",
    "require_any_authenticated",
    "verify_agent_api_key"
]
