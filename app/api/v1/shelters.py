from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_optional_user
from app.core.response import success_response
from app.models.user import User
from app.schemas.shelter import ShelterCreate, ShelterUpdate, ShelterResponse
from app.services.resource_service import ResourceService

router = APIRouter(prefix="/shelters", tags=["Shelters & Evacuation"])


@router.get("", summary="List All Active Shelters")
def list_shelters(db: Session = Depends(get_db)):
    shelters = ResourceService.get_all_shelters(db)
    results = []
    for s in shelters:
        avail = max(0, s.capacity - s.occupied)
        results.append(ShelterResponse(
            id=s.id,
            name=s.name,
            description=s.description,
            latitude=s.latitude,
            longitude=s.longitude,
            address=s.address,
            capacity=s.capacity,
            occupied=s.occupied,
            available_capacity=avail,
            status=s.status,
            is_private=s.is_private,
            managed_by=s.managed_by,
            distance_km=0.0,
            created_at=s.created_at,
            updated_at=s.updated_at
        ))
    return success_response(data=results, message=f"Retrieved {len(results)} shelters")


@router.get("/nearby", summary="Find Nearby Emergency Shelters")
def get_nearby_shelters(
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0, description="User latitude"),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0, description="User longitude"),
    radius: Optional[float] = Query(None, gt=0, le=500.0, description="Radius in km (alias for radius_km)"),
    radius_km: Optional[float] = Query(None, gt=0, le=500.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    """
    Returns verified disaster shelters within the given radius, calculated via Haversine distance,
    sorted from nearest to furthest with real-time available capacity.
    If coordinates are not provided, returns all active shelters.
    """
    if latitude is None or longitude is None:
        return list_shelters(db=db)

    effective_radius = 15.0
    if isinstance(radius_km, (int, float)):
        effective_radius = float(radius_km)
    elif isinstance(radius, (int, float)):
        effective_radius = float(radius)

    shelters = ResourceService.get_nearby_shelters(db, latitude, longitude, effective_radius)
    return success_response(data=shelters, message=f"Found {len(shelters)} shelters within {effective_radius} km")


@router.get("/{id}", summary="Get Shelter Details")
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


@router.post("", summary="Create Emergency Shelter", status_code=status.HTTP_201_CREATED)
def create_shelter(
    data: ShelterCreate,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Registers a new government or private disaster shelter.
    """
    shelter = ResourceService.create_shelter(db, data, current_user)
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
    return success_response(data=resp, message="Shelter created successfully", status_code=status.HTTP_201_CREATED)


@router.patch("/{id}", summary="Update Shelter Details or Capacity")
def update_shelter(
    id: str,
    data: ShelterUpdate,
    db: Session = Depends(get_db)
):
    """
    Updates status, occupied count, or total capacity of a disaster shelter.
    """
    shelter = ResourceService.update_shelter(db, id, data)
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
    return success_response(data=resp, message="Shelter updated successfully")

