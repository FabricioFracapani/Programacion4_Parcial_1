from fastapi import APIRouter, Depends, Request, Response
from sqlmodel import Session
from app.core.database import get_session
from app.modules.auth.schemas import LoginRequest, RegisterRequest, AuthResponse
from app.modules.auth.service import AuthService
from app.modules.auth.dependencies import get_current_user

router = APIRouter(tags=["Auth"])


def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    return AuthService(session)


@router.post("/login", response_model=AuthResponse, summary="Iniciar sesion")
def login(
    data: LoginRequest,
    response: Response,
    svc: AuthService = Depends(get_auth_service),
):
    return svc.login(data, response)


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=201,
    summary="Registrar usuario",
)
def register(
    data: RegisterRequest,
    response: Response,
    svc: AuthService = Depends(get_auth_service),
):
    return svc.register(data, response)


@router.post("/refresh", response_model=AuthResponse, summary="Renovar tokens")
def refresh(
    request: Request,
    response: Response,
    svc: AuthService = Depends(get_auth_service),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No hay refresh token",
        )
    return svc.refresh(refresh_token, response)


@router.post("/logout", summary="Cerrar sesion")
def logout(
    request: Request,
    response: Response,
    svc: AuthService = Depends(get_auth_service),
):
    refresh_token = request.cookies.get("refresh_token")
    return svc.logout(response, refresh_token)


@router.get("/me", response_model=AuthResponse, summary="Obtener usuario actual")
def me(
    user: dict = Depends(get_current_user),
    svc: AuthService = Depends(get_auth_service),
):
    return svc.me(user)
