from sqlalchemy import Column, String, DateTime, DECIMAL, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    push_token = Column(String(255), nullable=True)
    ultima_latitud = Column(DECIMAL(10, 8), nullable=True)
    ultima_longitud = Column(DECIMAL(11, 8), nullable=True)
    ultima_conexion = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    deseos = relationship("Deseo", back_populates="usuario")
