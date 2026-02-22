from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional
from decimal import Decimal

class UsuarioBase(BaseModel):
    email: EmailStr
    push_token: Optional[str] = None
    ultima_latitud: Optional[Decimal] = None
    ultima_longitud: Optional[Decimal] = None

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioUpdate(BaseModel):
    push_token: Optional[str] = None
    ultima_latitud: Optional[Decimal] = None
    ultima_longitud: Optional[Decimal] = None
    ultima_conexion: Optional[datetime] = None

class UsuarioResponse(UsuarioBase):
    id: UUID
    ultima_conexion: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
