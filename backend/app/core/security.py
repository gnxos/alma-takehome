import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Cookie, HTTPException, status

from app.core import config

ALGORITHM = "HS256"


def verify_credentials(email: str, password: str) -> bool:
    if email.strip().lower() != config.ATTORNEY_EMAIL.strip().lower():
        return False
    return secrets.compare_digest(
        password.encode(),
        config.ATTORNEY_PASSWORD.encode(),
    )


def create_access_token(email: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": email,
        "iat": now,
        "exp": now + timedelta(minutes=config.JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm=ALGORITHM)


def get_current_attorney_email(
    access_token: Optional[str] = Cookie(default=None, alias=config.AUTH_COOKIE_NAME),
) -> str:
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    try:
        payload = jwt.decode(
            access_token,
            config.JWT_SECRET,
            algorithms=[ALGORITHM],
        )
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        ) from exc

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )
    return email
