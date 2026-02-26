from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from . import service, dto

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=dto.LoginResponse)
def login(datos: dto.LoginRequest, db: Session = Depends(get_db)):
    usuario = service.autenticar_usuario(db, email=datos.email, password=datos.password)
    if not usuario:
        raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
    return {
        "mensaje": "Login exitoso",
        "usuario_id": usuario.id,
        "email": usuario.email
    }
