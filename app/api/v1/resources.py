from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.response import success_response
from app.api.v1.shelters import get_nearby_shelters
from app.api.v1.hospitals import get_nearby_hospitals
from app.api.v1.relief_centers import get_nearby_relief_centers

router = APIRouter(prefix="/resources", tags=["Emergency Resource Aliases"])


@router.get("/shelters", summary="Resource Alias: Shelters")
def resource_shelters(
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0),
    radius_km: Optional[float] = Query(None, gt=0, le=500.0),
    db: Session = Depends(get_db)
):
    return get_nearby_shelters(latitude=latitude, longitude=longitude, radius_km=radius_km, db=db)


@router.get("/hospitals", summary="Resource Alias: Hospitals")
def resource_hospitals(
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0),
    radius_km: Optional[float] = Query(None, gt=0, le=500.0),
    db: Session = Depends(get_db)
):
    return get_nearby_hospitals(latitude=latitude, longitude=longitude, radius_km=radius_km, db=db)


@router.get("/relief-centers", summary="Resource Alias: Relief Centers")
def resource_relief_centers(
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0),
    radius_km: Optional[float] = Query(None, gt=0, le=500.0),
    db: Session = Depends(get_db)
):
    return get_nearby_relief_centers(latitude=latitude, longitude=longitude, radius_km=radius_km, db=db)
