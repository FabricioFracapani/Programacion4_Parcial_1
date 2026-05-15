from fastapi import Request, HTTPException, status, Depends
from jose import JWTError

from app.core.security import verify_token


async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
        )
    try:
        payload = verify_token(token, expected_type="access")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
        )
    return {
        "id": payload.get("sub"),
        "email": payload.get("email"),
        "roles": payload.get("roles", []),
    }


def require_role(*roles: str):
    async def role_checker(user: dict = Depends(get_current_user)) -> dict:
        user_roles = user.get("roles", [])
        if not any(r in user_roles for r in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permisos insuficientes",
            )
        return user

    return role_checker
