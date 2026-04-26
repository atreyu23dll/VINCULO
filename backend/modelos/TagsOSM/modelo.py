from sqlalchemy import Column, String, Integer
from database import Base

class TagOSM(Base):
    __tablename__ = "tags_osm"

    id = Column(Integer, primary_key=True, index=True)
    nombre_humano = Column(String, unique=True, index=True, nullable=False) # Ej: "Panadería"
    llave_osm = Column(String, nullable=False) # Ej: "shop"
    valor_osm = Column(String, nullable=False) # Ej: "bakery"
    descripcion = Column(String, nullable=True)

    def __repr__(self):
        return f"<TagOSM(nombre='{self.nombre_humano}', osm='{self.llave_osm}={self.valor_osm}')>"
