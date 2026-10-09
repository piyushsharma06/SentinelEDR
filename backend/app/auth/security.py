"""Security utilities: password hashing, JWT encoding/decoding, and API key management."""

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import jwt
from app.config import settings

PBKDF2_ITERATIONS = 200_000


def hash_password(password: str) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with a unique random salt."""
    salt = secrets.token_bytes(16)
    hash_bytes = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return f"pbkdf2_sha256${PBKDF2_ITERATIONS}${salt.hex()}${hash_bytes.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against stored PBKDF2-HMAC-SHA256 hash."""
    try:
        parts = hashed_password.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = bytes.fromhex(parts[2])
        expected_hash = bytes.fromhex(parts[3])
        calculated_hash = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(calculated_hash, expected_hash)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except jwt.PyJWTError:
        return None


def generate_agent_api_key() -> Tuple[str, str, str]:
    """
    Generate a secure random API key for an agent.
    Returns: (raw_api_key, key_hash, prefix)
    """
    raw_key = f"sentinel_agent_{secrets.token_urlsafe(32)}"
    key_hash = hash_api_key(raw_key)
    prefix = raw_key[:16]
    return raw_key, key_hash, prefix


def hash_api_key(api_key: str) -> str:
    """Compute SHA-256 hash of raw API key for secure persistence."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()
