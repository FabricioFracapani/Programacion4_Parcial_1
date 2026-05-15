import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status, Response
from sqlmodel import Session, select

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    set_auth_cookies,
    clear_auth_cookies,
)
from app.modules.auth.models import Usuario, RefreshToken, UsuarioRol
from app.modules.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    UserPublic,
    AuthResponse,
)
from app.modules.auth.unit_of_work import AuthUnitOfWork


class AuthService:
    def __init__(self, session: Session):
        self._session = session

    def _build_user_public(self, user: Usuario) -> UserPublic:
        roles = [ur.rol_codigo for ur in (user.roles or [])]
        return UserPublic(
            id=user.id,
            nombre=user.nombre,
            apellido=user.apellido,
            email=user.email,
            celular=user.celular,
            roles=roles,
        )

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def _create_tokens_and_set_cookies(
        self,
        response: Response,
        user: Usuario,
        uow: AuthUnitOfWork,
    ) -> None:
        roles = [ur.rol_codigo for ur in (user.roles or [])]
        access_token = create_access_token({
            "sub": user.id,
            "email": user.email,
            "roles": roles,
        })
        refresh_token_str = create_refresh_token({"sub": user.id})

        token_hash = self._hash_token(refresh_token_str)
        rt = RefreshToken(
            usuario_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        uow.refresh_tokens.add(rt)

        set_auth_cookies(response, access_token, refresh_token_str)

    def login(self, data: LoginRequest, response: Response) -> AuthResponse:
        with AuthUnitOfWork(self._session) as uow:
            user = uow.usuarios.get_by_email(data.email)
            if not user or not verify_password(data.password, user.password_hash):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales invalidas",
                )

            self._create_tokens_and_set_cookies(response, user, uow)

            return AuthResponse(
                message="Inicio de sesion exitoso",
                user=self._build_user_public(user),
            )

    def register(self, data: RegisterRequest, response: Response) -> AuthResponse:
        with AuthUnitOfWork(self._session) as uow:
            existing = uow.usuarios.get_by_email(data.email)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="El email ya esta registrado",
                )

            user = Usuario(
                nombre=data.nombre,
                apellido=data.apellido,
                email=data.email,
                celular=data.celular,
                password_hash=hash_password(data.password),
            )
            uow.usuarios.add(user)

            uow.usuarios_roles.assign_role(user.id, "CLIENT")

            self._create_tokens_and_set_cookies(response, user, uow)

        return AuthResponse(
            message="Registro exitoso",
            user=self._build_user_public(user),
        )

    def refresh(self, refresh_token_str: str, response: Response) -> AuthResponse:
        try:
            payload = verify_token(refresh_token_str, expected_type="refresh")
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token invalido",
            )

        with AuthUnitOfWork(self._session) as uow:
            token_hash = self._hash_token(refresh_token_str)
            rt = uow.refresh_tokens.get_valid_by_hash(token_hash)
            if rt is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token revocado o expirado",
                )

            rt.revoked_at = datetime.utcnow()
            self._session.add(rt)

            user = uow.usuarios.get_by_id(payload["sub"])
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario no encontrado",
                )

            self._create_tokens_and_set_cookies(response, user, uow)

            return AuthResponse(
                message="Token renovado",
                user=self._build_user_public(user),
            )

    def logout(self, response: Response, refresh_token_str: Optional[str] = None) -> dict:
        if refresh_token_str:
            with AuthUnitOfWork(self._session) as uow:
                token_hash = self._hash_token(refresh_token_str)
                uow.refresh_tokens.revoke_by_hash(token_hash)

        clear_auth_cookies(response)
        return {"success": True, "message": "Sesion cerrada"}

    def me(self, user_data: dict) -> AuthResponse:
        with AuthUnitOfWork(self._session) as uow:
            user = uow.usuarios.get_by_id(user_data["id"])
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Usuario no encontrado",
                )
            return AuthResponse(user=self._build_user_public(user))
