from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from . import service, dto

router = APIRouter(prefix="/ubicaciones", tags=["Ubicaciones"])

@router.post("/", response_model=dto.UbicacionDeseoResponse)
def create_ubicacion(ubicacion: dto.UbicacionDeseoCreate, db: Session = Depends(get_db)):
    return service.create_ubicacion(db=db, ubicacion=ubicacion)

@router.get("/deseo/{deseo_id}", response_model=List[dto.UbicacionDeseoResponse])
def read_ubicaciones_deseo(deseo_id: UUID, db: Session = Depends(get_db)):
    return service.get_ubicaciones_by_deseo(db, deseo_id=deseo_id)

@router.patch("/{ubicacion_id}/notificar", response_model=dto.UbicacionDeseoResponse)
def notificar_ubicacion(ubicacion_id: UUID, ya_notificado: bool = True, db: Session = Depends(get_db)):
    db_ubicacion = service.update_notificacion(db, ubicacion_id=ubicacion_id, notificado=ya_notificado)
    if db_ubicacion is None:
        raise HTTPException(status_code=404, detail="Ubicacion not found")
    return db_ubicacion

@router.delete("/{ubicacion_id}")
def delete_ubicacion(ubicacion_id: UUID, db: Session = Depends(get_db)):
    success = service.delete_ubicacion(db, ubicacion_id=ubicacion_id)
    if not success:
        raise HTTPException(status_code=404, detail="Ubicacion not found")
    return {"detail": "Ubicacion deleted"}
