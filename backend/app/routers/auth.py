from fastapi import APIRouter, Depends, HTTPException, Response, status

from app import config, schemas
from app.auth import create_access_token, get_current_attorney_email, verify_credentials

router = APIRouter(tags=["auth"])


@router.post("/login", response_model=schemas.AttorneyOut)
def login(payload: schemas.LoginRequest, response: Response):
    if not verify_credentials(payload.email, payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    token = create_access_token(config.ATTORNEY_EMAIL)
    response.set_cookie(
        key=config.AUTH_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=config.COOKIE_SECURE,
        samesite=config.COOKIE_SAMESITE,
        max_age=config.JWT_EXPIRE_MINUTES * 60,
        path="/",
    )
    return schemas.AttorneyOut(email=config.ATTORNEY_EMAIL)


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key=config.AUTH_COOKIE_NAME,
        path="/",
        secure=config.COOKIE_SECURE,
        samesite=config.COOKIE_SAMESITE,
    )
    return {"detail": "Logged out"}


@router.get("/auth/me", response_model=schemas.AttorneyOut)
def me(email: str = Depends(get_current_attorney_email)):
    return schemas.AttorneyOut(email=email)
