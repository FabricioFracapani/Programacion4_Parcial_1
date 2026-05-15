# app/modules/auth/schemas.py
from typing import Optional
from sqlmodel import SQLModel, Field


class LoginRequest(SQLModel):
    username: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=3, max_length=100)


class RegisterRequest(SQLModel):
    username: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=3, max_length=100)


class TokenResponse(SQLModel):
    access_token: str
    token_type: str = "bearer"


class UserPublic(SQLModel):
    id: int
    username: str
    rol: str
