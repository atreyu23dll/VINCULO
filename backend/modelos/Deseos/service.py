from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from .modelo import Deseo
from .dto import DeseoCreate, DeseoUpdate
# Importamos la tarea de celery (usamos import local para evitar circulares)
from tasks import procesar_deseo_completo

def get_deseo(db: Session, deseo_id: UUID):
    return db.query(Deseo).options(joinedload(Deseo.ubicaciones)).filter(Deseo.id == deseo_id).first()

def get_deseos_by_usuario(db: Session, usuario_id: UUID):
    return db.query(Deseo).options(joinedload(Deseo.ubicaciones)).filter(Deseo.usuario_id == usuario_id).order_by(Deseo.created_at.desc()).all()

def create_deseo(db: Session, deseo: DeseoCreate):
    # Creamos el registro con estado inicial "nuevo"
    db_deseo = Deseo(
        usuario_id=deseo.usuario_id,
        texto_original=deseo.texto_original,
        tag_osm=None, # Lo pondrá Celery
        estado="nuevo",
        prioridad=deseo.prioridad,
        latitud_usuario=deseo.latitud_usuario,
        longitud_usuario=deseo.longitud_usuario,
        radio_busqueda_metros=deseo.radio_busqueda_metros or 5000
    )
    db.add(db_deseo)
    db.commit()
    db.refresh(db_deseo)

    # 🚀 DISPARAMOS LA TAREA ASÍNCRONA
    # Pasamos el ID como string porque Celery prefiere tipos simples para serializar
    procesar_deseo_completo.delay(str(db_deseo.id))
    
    return db_deseo

def update_deseo(db: Session, deseo_id: UUID, deseo_update: DeseoUpdate):
    db_deseo = get_deseo(db, deseo_id)
    if db_deseo:
        update_data = deseo_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_deseo, key, value)
        db.commit()
        db.refresh(db_deseo)
        return get_deseo(db, deseo_id)
    return db_deseo

def delete_deseo(db: Session, deseo_id: UUID):
    db_deseo = db.query(Deseo).filter(Deseo.id == deseo_id).first()
    if db_deseo:
        db.delete(db_deseo)
        db.commit()
        return True
    return False
