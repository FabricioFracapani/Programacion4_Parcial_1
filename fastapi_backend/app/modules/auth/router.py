# app/modules/auth/router.py
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserPublic
from app.modules.auth.service import AuthService
from app.modules.auth.dependencies import get_current_user

router = APIRouter(tags=["Auth"])


def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    return AuthService(session)


@router.post("/login", response_model=TokenResponse, summary="Iniciar sesión")
def login(data: LoginRequest, svc: AuthService = Depends(get_auth_service)):
    return svc.login(data)


@router.post("/register", response_model=UserPublic, status_code=201, summary="Registrar usuario")
def register(data: RegisterRequest, svc: AuthService = Depends(get_auth_service)):
    return svc.register(data)


@router.get("/me", response_model=UserPublic, summary="Obtener usuario actual")
def me(
    user: dict = Depends(get_current_user),
    svc: AuthService = Depends(get_auth_service),
):
    return svc.get_current_user(user)
