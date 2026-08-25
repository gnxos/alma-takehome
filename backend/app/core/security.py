import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import Cookie, HTTPException, status

from app.core import config

ALGORITHM = "HS256"


def get_attorney_accounts() -> dict[str, str]:
    accounts = {
        email.lower(): info["password"]
        for email, info in config.DEFAULT_ATTORNEYS.items()
    }
    if config.ATTORNEY_EMAIL:
        accounts[config.ATTORNEY_EMAIL.strip().lower()] = config.ATTORNEY_PASSWORD
    return accounts


def verify_credentials(email: str, password: str) -> bool:
    accounts = get_attorney_accounts()
    normalized_email = email.strip().lower()
    if normalized_email not in accounts:
        return False
    expected_password = accounts[normalized_email]
    return secrets.compare_digest(
        password.encode(),
        expected_password.encode(),
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
