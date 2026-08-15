from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user, get_optional_user
from app.core.response import success_response
from app.models.user import User, UserRole
from app.schemas.sos import SOSCreate, SOSUpdate, SOSResponse
from app.services.sos_service import SOSService

router = APIRouter(prefix="/sos", tags=["SOS Alerts"])


@router.get("", summary="List All Active SOS Alerts")
def list_sos(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 2000,
    db: Session = Depends(get_db)
):
    """
    Returns active emergency SOS alerts for tactical live feeds, map markers, and responders.
    """
    sos_list = SOSService.get_all_sos(db, status_filter=status, skip=skip, limit=limit)
    response_data = [SOSResponse.model_validate(s) for s in sos_list]
    return success_response(data=response_data, message=f"Retrieved {len(response_data)} SOS alerts")


@router.post("", summary="Create Emergency SOS Alert", status_code=status.HTTP_201_CREATED)
def create_sos(
    sos_data: SOSCreate,
    current_user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Submits an emergency SOS alert.
    If authenticated, links the SOS to the citizen profile.
    Can also be created anonymously or on behalf of an offline victim device.
    """
    sos = SOSService.create_sos(db, sos_data, current_user)
    response_data = SOSResponse.model_validate(sos)
    return success_response(
        data=response_data,
        message="SOS alert registered successfully. Emergency authorities have been notified.",
        status_code=status.HTTP_201_CREATED
    )


@router.get("/my", summary="Get Current Citizen's SOS Alerts")
def get_my_sos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves all SOS alerts submitted by the authenticated citizen.
    """
    sos_list = SOSService.get_citizen_sos_list(db, current_user.id)
    response_data = [SOSResponse.model_validate(s) for s in sos_list]
    return success_response(data=response_data, message="Citizen SOS history retrieved")


@router.get("/{id}", summary="Get SOS Alert Details")
def get_sos_by_id(
    id: str,
    current_user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves detailed information for a specific SOS alert.
    """
    sos = SOSService.get_sos_by_id(db, id)
    if not sos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SOS alert with ID {id} was not found"
        )

    # If user is a citizen, verify ownership
    if current_user and current_user.role == UserRole.CITIZEN:
        if sos.citizen_id and sos.citizen_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view this private SOS alert"
            )

    response_data = SOSResponse.model_validate(sos)
    return success_response(data=response_data, message="SOS details retrieved")


@router.patch("/{id}", summary="Update SOS Alert Status")
def update_sos(
    id: str,
    update_data: SOSUpdate,
    db: Session = Depends(get_db)
):
    """
    Updates status or severity of an emergency SOS alert.
    """
    sos = SOSService.update_sos(db, id, update_data)
    if not sos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SOS alert with ID {id} was not found"
        )
    return success_response(data=SOSResponse.model_validate(sos), message="SOS alert updated successfully")

