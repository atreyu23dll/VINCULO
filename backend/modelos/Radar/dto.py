from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class RadarCheckRequest(BaseModel):
    usuario_id: UUID
    latitude: float
    longitude: float
    radius_meters: Optional[int] = 500

class RadarMatch(BaseModel):
    lugar_nombre: str
    deseo_id: UUID
    deseo_texto: str
    lat: float
    lon: float

class RadarCheckResponse(BaseModel):
    matches: List[RadarMatch]
