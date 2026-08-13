from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.response import success_response
from app.schemas.hospital import HospitalResponse
from app.services.resource_service import ResourceService

router = APIRouter(prefix="/hospitals", tags=["Hospitals & Emergency Medical"])


@router.get("", summary="List All Hospitals")
def list_hospitals(db: Session = Depends(get_db)):
    hospitals = ResourceService.get_all_hospitals(db)
    results = [
        HospitalResponse(
            id=h.id,
            name=h.name,
            type=h.type,
            latitude=h.latitude,
            longitude=h.longitude,
            address=h.address,
            emergency_available=h.emergency_available,
            total_beds=h.total_beds,
            available_beds=h.available_beds,
            icu_total=h.icu_total,
            icu_available=h.icu_available,
            managed_by=h.managed_by,
            distance_km=0.0,
            created_at=h.created_at,
            updated_at=h.updated_at
        ) for h in hospitals
    ]
    return success_response(data=results, message=f"Retrieved {len(results)} hospitals")


@router.get("/nearby", summary="Find Nearby Hospitals and Available Beds")
def get_nearby_hospitals(
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0, description="User latitude"),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0, description="User longitude"),
    radius: Optional[float] = Query(None, gt=0, le=500.0, description="Radius in km (alias for radius_km)"),
    radius_km: Optional[float] = Query(None, gt=0, le=500.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    """
    Returns government and private hospitals within the specified radius,
    sorted by distance with real-time available general and ICU bed counts.
    If coordinates are not provided, returns all hospitals.
    """
    if latitude is None or longitude is None:
        return list_hospitals(db=db)

    effective_radius = 15.0
    if isinstance(radius_km, (int, float)):
        effective_radius = float(radius_km)
    elif isinstance(radius, (int, float)):
        effective_radius = float(radius)

    hospitals = ResourceService.get_nearby_hospitals(db, latitude, longitude, effective_radius)
    return success_response(data=hospitals, message=f"Found {len(hospitals)} hospitals within {effective_radius} km")


@router.get("/{id}", summary="Get Hospital Bed Details")
def get_hospital_by_id(
    id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves full details for a hospital including emergency triage and bed availability.
    """
    h = ResourceService.get_hospital_by_id(db, id)
    if not h:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hospital with ID {id} was not found"
        )
    resp = HospitalResponse(
        id=h.id,
        name=h.name,
        type=h.type,
        latitude=h.latitude,
        longitude=h.longitude,
        address=h.address,
        emergency_available=h.emergency_available,
        total_beds=h.total_beds,
        available_beds=h.available_beds,
        icu_total=h.icu_total,
        icu_available=h.icu_available,
        managed_by=h.managed_by,
        created_at=h.created_at,
        updated_at=h.updated_at
    )
    return success_response(data=resp, message="Hospital details retrieved")
