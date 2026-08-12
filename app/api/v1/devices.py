from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_optional_user
from app.core.response import success_response
from app.models.user import User
from app.schemas.device import DeviceRegisterRequest, DeviceResponse
from app.services.device_service import DeviceService

router = APIRouter(prefix="/devices", tags=["Mesh & Gateway Devices"])


@router.post("/register", summary="Register or Heartbeat Device", status_code=status.HTTP_200_OK)
def register_device(
    device_data: DeviceRegisterRequest,
    current_user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Registers a new mesh node / gateway device or updates its last seen telemetry,
    battery percentage, and mesh hop count.
    """
    device = DeviceService.register_or_update_device(db, device_data, current_user)
    return success_response(
        data=DeviceResponse.model_validate(device),
        message="Device telemetry registered successfully"
    )


@router.get("", summary="List All Registered Devices")
def list_devices(
    device_type: str = Query(None, description="Filter by device_type (e.g. GATEWAY, MESH_NODE)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Returns all registered devices, paginated.
    """
    devices = DeviceService.get_all_devices(db, device_type, skip, limit)
    return success_response(
        data=[DeviceResponse.model_validate(d) for d in devices],
        message=f"Retrieved {len(devices)} devices"
    )


@router.get("/nearby", summary="Find Nearby Devices")
def get_nearby_devices(
    lat: float = Query(None, description="User latitude"),
    lng: float = Query(None, description="User longitude"),
    radius_km: float = Query(15.0, gt=0, le=500.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    """
    Returns devices within the given radius, calculated via Haversine distance,
    sorted from nearest to furthest. Falls back to all devices if no coords provided.
    """
    if lat is None or lng is None:
        return list_devices(device_type=None, skip=0, limit=100, db=db)
    
    devices = DeviceService.get_nearby_devices(db, lat, lng, radius_km)
    return success_response(
        data=[DeviceResponse.model_validate(d) for d in devices],
        message=f"Found {len(devices)} devices within {radius_km} km"
    )



@router.get("/{device_id}", summary="Get Device Status by Hardware ID")
def get_device_by_id(
    device_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves information and last seen timestamp for a specific mesh node or gateway.
    """
    device = DeviceService.get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID '{device_id}' was not found"
        )
    return success_response(data=DeviceResponse.model_validate(device), message="Device status retrieved")
