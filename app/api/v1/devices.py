from fastapi import APIRouter, Depends, HTTPException, status
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
