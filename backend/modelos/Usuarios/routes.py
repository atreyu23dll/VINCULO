from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from modelos.Usuarios.modelo import Usuario
from auth import get_current_user
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

class PushTokenSchema(BaseModel):
    push_token: str

class UbicacionSchema(BaseModel):
    latitud: float
    longitud: float

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/me/push-token")
async def actualizar_push_token(
    payload: PushTokenSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = uuid.UUID(current_user["sub"])
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.push_token = payload.push_token
    db.commit()
    print(f"✅ Push Token guardado para usuario {user.email}")
    return {"status": "ok"}

@router.post("/me/ubicacion")
async def actualizar_ubicacion(
    payload: UbicacionSchema,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = uuid.UUID(current_user["sub"])
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.ultima_latitud = payload.latitud
    user.ultima_longitud = payload.longitud
    db.commit()
    print(f"📍 Ubicación actualizada para {user.email}: {payload.latitud}, {payload.longitud}")
    return {"status": "ok"}
