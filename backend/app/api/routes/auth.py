from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.core import config
from app.core.security import (
    create_access_token,
    get_current_attorney_email,
    verify_credentials,
)
from app.schemas.auth import AttorneyOut, LoginRequest

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=AttorneyOut)
def login(payload: LoginRequest, response: Response) -> AttorneyOut:
    if not verify_credentials(payload.email, payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    normalized_email = payload.email.strip().lower()
    token = create_access_token(normalized_email)
    response.set_cookie(
        key=config.AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=config.COOKIE_SECURE,
        samesite=config.COOKIE_SAMESITE,
        max_age=config.JWT_EXPIRE_MINUTES * 60,
        path="/",
    )
    return AttorneyOut(email=normalized_email)


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie(
        key=config.AUTH_COOKIE_NAME,
        path="/",
        secure=config.COOKIE_SECURE,
        samesite=config.COOKIE_SAMESITE,
    )
    return {"detail": "Logged out"}


@router.get("/auth/me", response_model=AttorneyOut)
def me(email: str = Depends(get_current_attorney_email)) -> AttorneyOut:
    return AttorneyOut(email=email)
