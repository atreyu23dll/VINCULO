from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, UUID
from sqlalchemy.sql import func
import uuid
from database import Base

class Notificacion(Base):
    __tablename__ = "notificaciones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    
    mensaje = Column(String(500), nullable=False)
    leida = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, server_default=func.now())
