from sqlalchemy.orm import Session
from .modelo import UbicacionDeseo
from .dto import UbicacionDeseoCreate, UbicacionDeseoUpdate
from uuid import UUID
from geoalchemy2.shape import from_shape
from shapely.geometry import Point

def get_ubicacion(db: Session, ubicacion_id: UUID):
    return db.query(UbicacionDeseo).filter(UbicacionDeseo.id == ubicacion_id).first()

def get_ubicaciones_by_deseo(db: Session, deseo_id: UUID):
    return db.query(UbicacionDeseo).filter(UbicacionDeseo.deseo_id == deseo_id).all()

def create_ubicacion(db: Session, ubicacion: UbicacionDeseoCreate):
    # Asumiendo que ubicacion llega como "lat,lon" o "POINT(lon lat)"
    # Aquí simplificamos asumiendo que el DTO manda algo parseable
    # En producción usarías una utilidad para convertir WKT a Geometry
    db_ubicacion = UbicacionDeseo(
        deseo_id=ubicacion.deseo_id,
        osm_id=ubicacion.osm_id,
        nombre_lugar=ubicacion.nombre_lugar,
        ubicacion=ubicacion.ubicacion # GeoAlchemy2 acepta WKT strings
    )
    db.add(db_ubicacion)
    db.commit()
    db.refresh(db_ubicacion)
    return db_ubicacion

def update_notificacion(db: Session, ubicacion_id: UUID, notificado: bool):
    db_ubicacion = get_ubicacion(db, ubicacion_id)
    if db_ubicacion:
        db_ubicacion.ya_notificado = notificado
        if notificado:
            from datetime import datetime
            db_ubicacion.fecha_notificacion = datetime.now()
        db.commit()
        db.refresh(db_ubicacion)
    return db_ubicacion

def delete_ubicacion(db: Session, ubicacion_id: UUID):
    db_ubicacion = get_ubicacion(db, ubicacion_id)
    if db_ubicacion:
        db.delete(db_ubicacion)
        db.commit()
        return True
    return False
