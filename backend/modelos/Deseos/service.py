from sqlalchemy.orm import Session
from .modelo import Deseo
from .dto import DeseoCreate, DeseoUpdate
from uuid import UUID

def get_deseo(db: Session, deseo_id: UUID):
    return db.query(Deseo).filter(Deseo.id == deseo_id).first()

def get_deseos_by_usuario(db: Session, usuario_id: UUID):
    return db.query(Deseo).filter(Deseo.usuario_id == usuario_id).all()

def create_deseo(db: Session, deseo: DeseoCreate):
    db_deseo = Deseo(
        usuario_id=deseo.usuario_id,
        texto_original=deseo.texto_original,
        tag_osm=deseo.tag_osm,
        radio_busqueda_metros=deseo.radio_busqueda_metros
    )
    db.add(db_deseo)
    db.commit()
    db.refresh(db_deseo)
    return db_deseo

def update_deseo(db: Session, deseo_id: UUID, deseo_update: DeseoUpdate):
    db_deseo = get_deseo(db, deseo_id)
    if db_deseo:
        update_data = deseo_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_deseo, key, value)
        db.commit()
        db.refresh(db_deseo)
    return db_deseo

def delete_deseo(db: Session, deseo_id: UUID):
    db_deseo = get_deseo(db, deseo_id)
    if db_deseo:
        db.delete(db_deseo)
        db.commit()
        return True
    return False
