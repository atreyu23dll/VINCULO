from pydantic import BaseModel, ConfigDict, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class UbicacionDeseoSimple(BaseModel):
    id: UUID
    nombre_lugar: Optional[str]
    lat: float
    lon: float

    model_config = ConfigDict(from_attributes=True)

class DeseoBase(BaseModel):
    texto_original: str
    tag_osm: Optional[str] = None
    radio_busqueda_metros: Optional[int] = 5000
    prioridad: Optional[str] = "media"
    es_favorito: Optional[bool] = False
    latitud_usuario: Optional[float] = None
    longitud_usuario: Optional[float] = None

class DeseoCreate(DeseoBase):
    usuario_id: UUID

class DeseoUpdate(BaseModel):
    texto_original: Optional[str] = None
    tag_osm: Optional[str] = None
    estado: Optional[str] = None
    prioridad: Optional[str] = None
    es_favorito: Optional[bool] = None
    radio_busqueda_metros: Optional[int] = None
    latitud_usuario: Optional[float] = None
    longitud_usuario: Optional[float] = None

class DeseoResponse(DeseoBase):
    id: UUID
    usuario_id: UUID
    estado: str
    created_at: datetime
    updated_at: datetime
    ubicaciones: List[UbicacionDeseoSimple] = [] # Nueva lista de ubicaciones

    model_config = ConfigDict(from_attributes=True)
