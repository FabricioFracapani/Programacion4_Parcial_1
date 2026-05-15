# app/modules/auth/models.py
from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime


class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, max_length=100)
    password_hash: str
    rol: str = Field(default="USER")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)
