from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.response import success_response
from app.schemas.shelter import ShelterResponse
from app.services.resource_service import ResourceService

router = APIRouter(tags=["Shelters & Evacuation"])


@router.get("/shelters/nearby", summary="Find Nearby Emergency Shelters")
@router.get("/resources/shelters", summary="List Shelters for Resources")
def get_nearby_shelters(
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0, description="User latitude"),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0, description="User longitude"),
    radius: Optional[float] = Query(None, gt=0, le=500.0, description="Radius in km (alias for radius_km)"),
    radius_km: Optional[float] = Query(None, gt=0, le=500.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    """
    Returns verified disaster shelters.
    If coordinates are provided, filters via Haversine distance and sorts nearest-to-furthest.
    If coordinates are omitted, returns all open shelters with their available capacities.
    """
    if latitude is not None and longitude is not None:
        effective_radius = radius_km or radius or 15.0
        shelters = ResourceService.get_nearby_shelters(db, latitude, longitude, effective_radius)
        return success_response(data=shelters, message=f"Found {len(shelters)} shelters within {effective_radius} km")
    
    all_shelters = ResourceService.get_all_shelters(db)
    results = []
    for s in all_shelters:
        available_cap = max(0, s.capacity - s.occupied)
        results.append(ShelterResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            latitude=s.latitude,
            longitude=s.longitude,
            address=s.address,
            capacity=s.capacity,
            occupied=s.occupied,
            available_capacity=available_cap,
            status=s.status,
            is_private=s.is_private,
            managed_by=s.managed_by,
            distance_km=1.2,
            created_at=s.created_at,
            updated_at=s.updated_at
        ))
    return success_response(data=results, message=f"Retrieved {len(results)} emergency shelters")


@router.get("/shelters/{id}", summary="Get Shelter Details")
def get_shelter_by_id(
    id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves full details and capacity for a specific emergency shelter.
    """
    shelter = ResourceService.get_shelter_by_id(db, id)
    if not shelter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shelter with ID {id} was not found"
        )
    available_cap = max(0, shelter.capacity - shelter.occupied)
    resp = ShelterResponse(
        id=shelter.id,
        name=shelter.name,
        description=shelter.description,
        latitude=shelter.latitude,
        longitude=shelter.longitude,
        address=shelter.address,
        capacity=shelter.capacity,
        occupied=shelter.occupied,
        available_capacity=available_cap,
        status=shelter.status,
        is_private=shelter.is_private,
        managed_by=shelter.managed_by,
        created_at=shelter.created_at,
        updated_at=shelter.updated_at
    )
    return success_response(data=resp, message="Shelter details retrieved")
