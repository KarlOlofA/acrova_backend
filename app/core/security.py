from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.core.config import settings

_STATE_PURPOSE = "linkedin_oauth_state"


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    return payload["sub"]


def create_oauth_state_token(role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.oauth_state_expire_minutes)
    payload = {"role": role, "exp": expire, "purpose": _STATE_PURPOSE}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_oauth_state_token(token: str) -> dict[str, Any]:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    if payload.get("purpose") != _STATE_PURPOSE:
        raise ValueError("Token is not a valid OAuth state token")
    return payload
