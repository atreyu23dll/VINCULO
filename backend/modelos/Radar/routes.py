from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from . import service, dto

router = APIRouter(prefix="/api/radar", tags=["Radar"])

@router.post("/check", response_model=dto.RadarCheckResponse)
def check_radar(req: dto.RadarCheckRequest, db: Session = Depends(get_db)):
    try:
        matches = service.check_radar_matches(
            db=db, 
            usuario_id=req.usuario_id, 
            lat=req.latitude, 
            lon=req.longitude, 
            radius=req.radius_meters
        )
        return dto.RadarCheckResponse(matches=matches)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
