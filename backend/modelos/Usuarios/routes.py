from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from . import service, dto

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=dto.UsuarioResponse)
def create_usuario(usuario: dto.UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = service.get_usuario_by_email(db, email=usuario.email)
    if db_usuario:
        raise HTTPException(status_code=400, detail="Email already registered")
    return service.create_usuario(db=db, usuario=usuario)

@router.get("/", response_model=List[dto.UsuarioResponse])
def read_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    usuarios = service.get_usuarios(db, skip=skip, limit=limit)
    return usuarios

@router.get("/{usuario_id}", response_model=dto.UsuarioResponse)
def read_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    db_usuario = service.get_usuario(db, usuario_id=usuario_id)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario not found")
    return db_usuario

@router.patch("/{usuario_id}", response_model=dto.UsuarioResponse)
def update_usuario(usuario_id: UUID, usuario_update: dto.UsuarioUpdate, db: Session = Depends(get_db)):
    db_usuario = service.update_usuario(db, usuario_id=usuario_id, usuario_update=usuario_update)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario not found")
    return db_usuario

@router.delete("/{usuario_id}")
def delete_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    success = service.delete_usuario(db, usuario_id=usuario_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario not found")
    return {"detail": "Usuario deleted"}
