from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, BigInteger, UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from sqlalchemy.sql import func
import uuid
from database import Base

class UbicacionDeseo(Base):
    __tablename__ = "ubicaciones_deseo"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deseo_id = Column(UUID(as_uuid=True), ForeignKey("deseos.id"), nullable=False)
    osm_id = Column(BigInteger, nullable=False)
    nombre_lugar = Column(String(255), nullable=True)
    
    ubicacion = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    
    ya_notificado = Column(Boolean, default=False)
    fecha_notificacion = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    deseo = relationship("Deseo", back_populates="ubicaciones")
