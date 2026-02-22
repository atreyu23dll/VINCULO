from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, UUID
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
    estado = Column(String(50), default="pendiente") # 'pendiente', 'buscando', 'cumplido', 'cancelado'
    radio_busqueda_metros = Column(Integer, default=5000)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    usuario = relationship("Usuario", back_populates="deseos")
    ubicaciones = relationship("UbicacionDeseo", back_populates="deseo")
