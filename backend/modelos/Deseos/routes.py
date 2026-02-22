from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from . import service, dto

router = APIRouter(prefix="/deseos", tags=["Deseos"])

@router.post("/", response_model=dto.DeseoResponse)
def create_deseo(deseo: dto.DeseoCreate, db: Session = Depends(get_db)):
    return service.create_deseo(db=db, deseo=deseo)

@router.get("/usuario/{usuario_id}", response_model=List[dto.DeseoResponse])
def read_deseos_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    return service.get_deseos_by_usuario(db, usuario_id=usuario_id)

@router.get("/{deseo_id}", response_model=dto.DeseoResponse)
def read_deseo(deseo_id: UUID, db: Session = Depends(get_db)):
    db_deseo = service.get_deseo(db, deseo_id=deseo_id)
    if db_deseo is None:
        raise HTTPException(status_code=404, detail="Deseo not found")
    return db_deseo

@router.patch("/{deseo_id}", response_model=dto.DeseoResponse)
def update_deseo(deseo_id: UUID, deseo_update: dto.DeseoUpdate, db: Session = Depends(get_db)):
    db_deseo = service.update_deseo(db, deseo_id=deseo_id, deseo_update=deseo_update)
    if db_deseo is None:
        raise HTTPException(status_code=404, detail="Deseo not found")
    return db_deseo

@router.delete("/{deseo_id}")
def delete_deseo(deseo_id: UUID, db: Session = Depends(get_db)):
    success = service.delete_deseo(db, deseo_id=deseo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Deseo not found")
    return {"detail": "Deseo deleted"}
