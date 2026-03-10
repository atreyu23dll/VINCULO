from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, Any

class DeseoBase(BaseModel):
    texto_original: str
    tag_osm: Optional[str] = None
    radio_busqueda_metros: Optional[int] = 5000

class DeseoCreate(DeseoBase):
    usuario_id: UUID

class DeseoUpdate(BaseModel):
    texto_original: Optional[str] = None
    tag_osm: Optional[str] = None
    estado: Optional[str] = None
    radio_busqueda_metros: Optional[int] = None

class DeseoCompleteRequest(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None

class DeseoResponse(DeseoBase):
    id: UUID
    usuario_id: UUID
    estado: str
    fecha_completado: Optional[datetime] = None
    ubicacion_completado: Optional[Any] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
