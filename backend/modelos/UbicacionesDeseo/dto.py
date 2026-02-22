from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class UbicacionDeseoBase(BaseModel):
    osm_id: int
    nombre_lugar: Optional[str] = None
    # La ubicación se manejará como string WKT o similar para simplicidad en el DTO
    ubicacion: str 

class UbicacionDeseoCreate(UbicacionDeseoBase):
    deseo_id: UUID

class UbicacionDeseoUpdate(BaseModel):
    ya_notificado: Optional[bool] = None
    fecha_notificacion: Optional[datetime] = None

class UbicacionDeseoResponse(UbicacionDeseoBase):
    id: UUID
    deseo_id: UUID
    ya_notificado: bool
    fecha_notificacion: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
