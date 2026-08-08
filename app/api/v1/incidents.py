from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user, get_optional_user
from app.core.response import success_response
from app.models.user import User
from app.schemas.incident import IncidentCreate, IncidentResponse
from app.services.incident_service import IncidentService

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.post("", summary="Report a Disaster Incident", status_code=status.HTTP_201_CREATED)
def report_incident(
    incident_data: IncidentCreate,
    current_user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Submits a new disaster incident report (Flood, Fire, Landslide, Building Collapse, etc.)
    with location, severity, and optional evidence media URLs.
    """
    incident = IncidentService.create_incident(db, incident_data, current_user)
    response_data = IncidentResponse(
        id=incident.id,
        message_id=incident.message_id,
        reported_by=incident.reported_by,
        title=incident.title,
        description=incident.description,
        type=incident.type,
        latitude=incident.latitude,
        longitude=incident.longitude,
        severity=incident.severity,
        status=incident.status,
        media_urls=incident.media_urls,
        created_at=incident.created_at,
        updated_at=incident.updated_at
    )
    return success_response(
        data=response_data,
        message="Disaster incident reported successfully",
        status_code=status.HTTP_201_CREATED
    )


@router.get("/my", summary="Get Incidents Reported by Current User")
def get_my_incidents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves all incidents submitted by the authenticated citizen or volunteer.
    """
    incidents = IncidentService.get_citizen_incidents(db, current_user.id)
    response_data = [
        IncidentResponse(
            id=inc.id,
            message_id=inc.message_id,
            reported_by=inc.reported_by,
            title=inc.title,
            description=inc.description,
            type=inc.type,
            latitude=inc.latitude,
            longitude=inc.longitude,
            severity=inc.severity,
            status=inc.status,
            media_urls=inc.media_urls,
            created_at=inc.created_at,
            updated_at=inc.updated_at
        ) for inc in incidents
    ]
    return success_response(data=response_data, message="Reported incidents retrieved")


@router.get("/{id}", summary="Get Incident Details")
def get_incident_by_id(
    id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieves full details for a disaster incident report.
    """
    incident = IncidentService.get_incident_by_id(db, id)
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {id} was not found"
        )
    response_data = IncidentResponse(
        id=incident.id,
        message_id=incident.message_id,
        reported_by=incident.reported_by,
        title=incident.title,
        description=incident.description,
        type=incident.type,
        latitude=incident.latitude,
        longitude=incident.longitude,
        severity=incident.severity,
        status=incident.status,
        media_urls=incident.media_urls,
        created_at=incident.created_at,
        updated_at=incident.updated_at
    )
    return success_response(data=response_data, message="Incident details retrieved")
