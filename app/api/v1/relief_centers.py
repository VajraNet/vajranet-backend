from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.response import success_response
from app.schemas.relief_center import ReliefCenterResponse
from app.services.resource_service import ResourceService

router = APIRouter(prefix="/relief-centers", tags=["Relief & Supply Centers"])


@router.get("", summary="List All Relief Centers")
def list_relief_centers(db: Session = Depends(get_db)):
    centers = ResourceService.get_all_relief_centers(db)
    results = [
        ReliefCenterResponse(
            id=rc.id,
            name=rc.name,
            description=rc.description,
            latitude=rc.latitude,
            longitude=rc.longitude,
            address=rc.address,
            items_available=rc.items_available,
            status=rc.status,
            managed_by=rc.managed_by,
            distance_km=0.0,
            created_at=rc.created_at,
            updated_at=rc.updated_at
        ) for rc in centers
    ]
    return success_response(data=results, message=f"Retrieved {len(results)} relief centers")


@router.get("/nearby", summary="Find Nearby Relief and Supply Centers")
def get_nearby_relief_centers(
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0, description="User latitude"),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0, description="User longitude"),
    radius: Optional[float] = Query(None, gt=0, le=500.0, description="Radius in km (alias for radius_km)"),
    radius_km: Optional[float] = Query(None, gt=0, le=500.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    """
    Returns verified relief supply and distribution centers (Food, Water, Medicine, Emergency Kits),
    sorted by proximity via Haversine formula.
    If coordinates are not provided, returns all relief centers.
    """
    if latitude is None or longitude is None:
        return list_relief_centers(db=db)

    effective_radius = 15.0
    if isinstance(radius_km, (int, float)):
        effective_radius = float(radius_km)
    elif isinstance(radius, (int, float)):
        effective_radius = float(radius)

    centers = ResourceService.get_nearby_relief_centers(db, latitude, longitude, effective_radius)
    return success_response(data=centers, message=f"Found {len(centers)} relief centers within {effective_radius} km")


@router.get("/{id}", summary="Get Relief Center Details")
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
