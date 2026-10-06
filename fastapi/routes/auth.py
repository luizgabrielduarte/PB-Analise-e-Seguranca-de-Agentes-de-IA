from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from slowapi.util import get_remote_address
from sqlmodel import Session

from database import get_session
from models.auth import Token
from security.jwt import authenticate_user, create_access_token
from security.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/token", response_model=Token)
@limiter.limit("10/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session)
):
    user = authenticate_user(
        form_data.username,
        form_data.password,
        session
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(
        user.username,
        user.role
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }