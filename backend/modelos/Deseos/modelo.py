from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, UUID, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from database import Base

class Deseo(Base):
    __tablename__ = "deseos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    texto_original = Column(Text, nullable=False)
    tag_osm = Column(String(100), nullable=True)
    estado = Column(String(50), default="nuevo") 
    prioridad = Column(String(20), default="media") 
    es_favorito = Column(Boolean, default=False)
    radio_busqueda_metros = Column(Integer, default=5000)
    
    # Nuevas columnas para guardar la ubicación desde donde se pidió el deseo
    latitud_usuario = Column(Float, nullable=True)
    longitud_usuario = Column(Float, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    usuario = relationship("Usuario", back_populates="deseos")
    ubicaciones = relationship("UbicacionDeseo", back_populates="deseo", cascade="all, delete-orphan")
