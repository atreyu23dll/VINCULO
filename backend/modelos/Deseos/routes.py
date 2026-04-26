from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_user
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from . import service, dto

router = APIRouter(prefix="/deseos", tags=["Deseos"])

@router.post("/", response_model=dto.DeseoResponse)
def create_deseo(deseo: dto.DeseoBase, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Convertimos el diccionario del usuario de Keycloak en un objeto DeseoCreate
    # sacando el ID del usuario directamente del token
    deseo_data = dto.DeseoCreate(
        **deseo.model_dump(),
        usuario_id=current_user["sub"]
    )
    return service.create_deseo(db=db, deseo=deseo_data)

@router.get("/me", response_model=List[dto.DeseoResponse])
def read_my_deseos(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    return service.get_deseos_by_usuario(db, usuario_id=current_user["sub"])

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
def delete_deseo(deseo_id: UUID, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Opcional: Verificar que el deseo pertenezca al usuario antes de borrar
    db_deseo = service.get_deseo(db, deseo_id=deseo_id)
    if not db_deseo or str(db_deseo.usuario_id) != current_user["sub"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this desire")
    
    success = service.delete_deseo(db, deseo_id=deseo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Deseo not found")
    return {"detail": "Deseo deleted"}
