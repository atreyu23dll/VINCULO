from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from modelos.Notificaciones.modelo import Notificacion
from auth import get_current_user 
import uuid

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/me")
async def obtener_mis_notificaciones(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Buscamos notificaciones no leídas para el usuario actual
    user_id = uuid.UUID(current_user["sub"])
    notifs = db.query(Notificacion).filter(
        Notificacion.usuario_id == user_id,
        Notificacion.leida == False
    ).order_by(Notificacion.fecha_creacion.desc()).all()
    
    return notifs

@router.post("/{notif_id}/leer")
async def marcar_como_leida(
    notif_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    notif = db.query(Notificacion).filter(Notificacion.id == notif_id).first()
    if notif:
        notif.leida = True
        db.commit()
    return {"status": "ok"}
