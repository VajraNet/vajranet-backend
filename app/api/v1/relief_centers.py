from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.response import success_response
from app.schemas.relief_center import ReliefCenterResponse
from app.services.resource_service import ResourceService

router = APIRouter(tags=["Relief & Supply Centers"])


@router.get("/relief-centers/nearby", summary="Find Nearby Relief and Supply Centers")
@router.get("/resources/relief-centers", summary="List Relief Centers")
def get_nearby_relief_centers(
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0, description="User latitude"),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0, description="User longitude"),
    radius: Optional[float] = Query(None, gt=0, le=500.0, description="Radius in km (alias for radius_km)"),
    radius_km: Optional[float] = Query(None, gt=0, le=500.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    """
    Returns relief distribution centers (Food, Water, Medicine, Emergency Kits).
    If coordinates are supplied, sorts by proximity via Haversine.
    If coordinates are omitted, returns all active relief centers.
    """
    if latitude is not None and longitude is not None:
        effective_radius = radius_km or radius or 15.0
        centers = ResourceService.get_nearby_relief_centers(db, latitude, longitude, effective_radius)
        return success_response(data=centers, message=f"Found {len(centers)} relief centers within {effective_radius} km")

    all_rc = ResourceService.get_all_relief_centers(db)
    results = []
    for rc in all_rc:
        results.append(ReliefCenterResponse(
            id=rc.id,
            name=rc.name,
            description=rc.description,
            latitude=rc.latitude,
            longitude=rc.longitude,
            address=rc.address,
            items_available=rc.items_available,
            status=rc.status,
            managed_by=rc.managed_by,
            distance_km=1.8,
            created_at=rc.created_at,
            updated_at=rc.updated_at
        ))
    return success_response(data=results, message=f"Retrieved {len(results)} relief distribution centers")


@router.get("/relief-centers/{id}", summary="Get Relief Center Details")
def get_relief_center_by_id(
    id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves full details for a disaster relief distribution center.
    """
    rc = ResourceService.get_relief_center_by_id(db, id)
    if not rc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relief center with ID {id} was not found"
        )
    resp = ReliefCenterResponse(
        id=rc.id,
        name=rc.name,
        description=rc.description,
        latitude=rc.latitude,
        longitude=rc.longitude,
        address=rc.address,
        items_available=rc.items_available,
        status=rc.status,
        managed_by=rc.managed_by,
        created_at=rc.created_at,
        updated_at=rc.updated_at
    )
    return success_response(data=resp, message="Relief center details retrieved")
