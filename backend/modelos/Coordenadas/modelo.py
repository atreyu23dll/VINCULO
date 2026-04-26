from sqlalchemy import Column, DateTime, ForeignKey, UUID, DECIMAL
from sqlalchemy.sql import func
import uuid
from database import Base

class Coordenada(Base):
    __tablename__ = "coordenadas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("usuarios.id"), nullable=False)
    
    # Usamos DECIMAL para máxima precisión en GPS (o podrías usar Geometry POINT)
    latitud = Column(DECIMAL(10, 8), nullable=False)
    longitud = Column(DECIMAL(11, 8), nullable=False)
    
    fecha_registro = Column(DateTime, server_default=func.now())

    # No necesitamos relación inversa obligatoria por ahora, 
    # pero ayuda a SQLAlchemy a entender el esquema.
