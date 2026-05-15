# app/modules/auth/service.py
from sqlmodel import Session
from fastapi import HTTPException, status
from app.modules.auth.models import Usuario
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, UserPublic
from app.modules.auth.repository import UsuarioRepository
from app.modules.auth.auth import hash_password, verify_password, create_token


class AuthService:
    def __init__(self, session: Session):
        self._session = session

    def login(self, data: LoginRequest) -> TokenResponse:
        repo = UsuarioRepository(self._session)
        user = repo.get_by_username(data.username)
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas",
            )
        token = create_token({"sub": user.username, "rol": user.rol, "id": user.id})
        return TokenResponse(access_token=token)

    def register(self, data: RegisterRequest) -> UserPublic:
        repo = UsuarioRepository(self._session)
        existing = repo.get_by_username(data.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El nombre de usuario ya existe",
            )
        user = Usuario(
            username=data.username,
            password_hash=hash_password(data.password),
            rol="USER",
        )
        repo.create(user)
        repo.commit()
        return UserPublic(id=user.id, username=user.username, rol=user.rol)

    def get_current_user(self, user_data: dict) -> UserPublic:
        repo = UsuarioRepository(self._session)
        user = repo.get_by_username(user_data["sub"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )
        return UserPublic(id=user.id, username=user.username, rol=user.rol)
