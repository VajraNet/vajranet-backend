from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import require_role, require_any_role
from app.core.response import success_response
from app.models.user import User, UserRole
from app.models.sos import SOSSeverity, SOSStatus
from app.models.incident import IncidentType, IncidentSeverity, IncidentStatus
from app.schemas.sos import SOSResponse, SOSUpdate
from app.schemas.incident import IncidentResponse, IncidentUpdate
from app.schemas.announcement import AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse
from app.schemas.shelter import ShelterCreate, ShelterUpdate, ShelterResponse
from app.schemas.hospital import HospitalCreate, HospitalUpdate, HospitalResponse
from app.schemas.relief_center import ReliefCenterCreate, ReliefCenterUpdate, ReliefCenterResponse
from app.schemas.dashboard import GovernmentOverviewResponse
from app.services.sos_service import SOSService
from app.services.incident_service import IncidentService
from app.services.announcement_service import AnnouncementService
from app.services.resource_service import ResourceService
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/government", tags=["Government Authority Management"])


# -----------------------------------------------------------------
# SOS ALERT MANAGEMENT
# -----------------------------------------------------------------
@router.get("/sos", summary="Government: View Incoming SOS Alerts")
def list_government_sos(
    status: Optional[SOSStatus] = Query(None, description="Filter by status: ACTIVE, ACKNOWLEDGED, IN_PROGRESS, RESOLVED"),
    severity: Optional[SOSSeverity] = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(require_any_role([UserRole.GOVERNMENT, UserRole.VOLUNTEER, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    sos_alerts = SOSService.get_all_sos(db, status_filter=status, severity_filter=severity, skip=skip, limit=limit)
    response_data = [SOSResponse.model_validate(s) for s in sos_alerts]
    return success_response(data=response_data, message=f"Retrieved {len(response_data)} SOS alerts")


@router.patch("/sos/{id}", summary="Government & Responder: Update SOS Status or Severity")
def update_government_sos(
    id: str,
    update_data: SOSUpdate,
    current_user: User = Depends(require_any_role([UserRole.GOVERNMENT, UserRole.VOLUNTEER, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    sos = SOSService.update_sos(db, id, update_data)
    if not sos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SOS alert with ID {id} was not found"
        )
    return success_response(data=SOSResponse.model_validate(sos), message="SOS alert updated successfully")


# -----------------------------------------------------------------
# INCIDENT MANAGEMENT
# -----------------------------------------------------------------
@router.get("/incidents", summary="Government: View Reported Incidents")
def list_government_incidents(
    type: Optional[IncidentType] = Query(None),
    severity: Optional[IncidentSeverity] = Query(None),
    status: Optional[IncidentStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(require_any_role([UserRole.GOVERNMENT, UserRole.VOLUNTEER, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    incidents = IncidentService.get_all_incidents(
        db, type_filter=type, severity_filter=severity, status_filter=status, skip=skip, limit=limit
    )
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
    return success_response(data=response_data, message=f"Retrieved {len(response_data)} incidents")


@router.patch("/incidents/{id}", summary="Government & Responder: Update Incident Status or Severity")
def update_government_incident(
    id: str,
    update_data: IncidentUpdate,
    current_user: User = Depends(require_any_role([UserRole.GOVERNMENT, UserRole.VOLUNTEER, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    inc = IncidentService.update_incident(db, id, update_data)
    if not inc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {id} was not found"
        )
    resp = IncidentResponse(
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
    )
    return success_response(data=resp, message="Incident updated successfully")


# -----------------------------------------------------------------
# ANNOUNCEMENTS
# -----------------------------------------------------------------
@router.get("/announcements", summary="Government: View All Announcements")
def list_government_announcements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(require_role(UserRole.GOVERNMENT)),
    db: Session = Depends(get_db)
):
    announcements = AnnouncementService.get_all_announcements(db, skip=skip, limit=limit)
    response_data = [AnnouncementResponse.model_validate(a) for a in announcements]
    return success_response(data=response_data, message="Government announcements retrieved")


@router.post("/announcements", summary="Government: Publish Emergency Announcement", status_code=status.HTTP_201_CREATED)
def publish_government_announcement(
    data: AnnouncementCreate,
    current_user: User = Depends(require_role(UserRole.GOVERNMENT)),
    db: Session = Depends(get_db)
):
    ann = AnnouncementService.create_announcement(db, data, current_user)
    return success_response(
        data=AnnouncementResponse.model_validate(ann),
        message="Emergency announcement published successfully",
        status_code=status.HTTP_201_CREATED
    )


@router.patch("/announcements/{id}", summary="Government: Update Emergency Announcement")
def update_government_announcement(
    id: str,
    data: AnnouncementUpdate,
    current_user: User = Depends(require_role(UserRole.GOVERNMENT)),
    db: Session = Depends(get_db)
):
    ann = AnnouncementService.update_announcement(db, id, data)
    if not ann:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Announcement with ID {id} was not found"
        )
    return success_response(data=AnnouncementResponse.model_validate(ann), message="Announcement updated successfully")


# -----------------------------------------------------------------
# SHELTERS
# -----------------------------------------------------------------
@router.post("/shelters", summary="Government: Create Official Shelter", status_code=status.HTTP_201_CREATED)
def create_government_shelter(
    data: ShelterCreate,
    current_user: User = Depends(require_role(UserRole.GOVERNMENT)),
    db: Session = Depends(get_db)
):
    data.is_private = False
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
    return success_response(
        data=resp,
        message="Government shelter created successfully",
        status_code=status.HTTP_201_CREATED
    )


@router.patch("/shelters/{id}", summary="Government: Update Shelter Capacity or Status")
def update_government_shelter(
    id: str,
    data: ShelterUpdate,
    current_user: User = Depends(require_role(UserRole.GOVERNMENT)),
    db: Session = Depends(get_db)
):
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


# -----------------------------------------------------------------
# HOSPITALS
# -----------------------------------------------------------------
@router.post("/hospitals", summary="Government: Add Hospital", status_code=status.HTTP_201_CREATED)
def create_government_hospital(
    data: HospitalCreate,
    current_user: User = Depends(require_role(UserRole.GOVERNMENT)),
    db: Session = Depends(get_db)
):
    h = ResourceService.create_hospital(db, data, current_user)
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
    return success_response(
        data=resp,
        message="Hospital registered successfully",
        status_code=status.HTTP_201_CREATED
    )


@router.patch("/hospitals/{id}", summary="Government: Update Hospital Bed Availability")
def update_government_hospital(
    id: str,
    data: HospitalUpdate,
    current_user: User = Depends(require_role(UserRole.GOVERNMENT)),
    db: Session = Depends(get_db)
):
    h = ResourceService.update_hospital(db, id, data)
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
    return success_response(data=resp, message="Hospital bed availability updated successfully")


# -----------------------------------------------------------------
# RELIEF CENTERS
# -----------------------------------------------------------------
@router.post("/relief-centers", summary="Government: Create Relief Distribution Center", status_code=status.HTTP_201_CREATED)
def create_government_relief_center(
    data: ReliefCenterCreate,
    current_user: User = Depends(require_role(UserRole.GOVERNMENT)),
    db: Session = Depends(get_db)
):
    rc = ResourceService.create_relief_center(db, data, current_user)
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
    return success_response(
        data=resp,
        message="Relief center created successfully",
        status_code=status.HTTP_201_CREATED
    )


@router.patch("/relief-centers/{id}", summary="Government: Update Relief Center Supplies or Status")
def update_government_relief_center(
    id: str,
    data: ReliefCenterUpdate,
    current_user: User = Depends(require_role(UserRole.GOVERNMENT)),
    db: Session = Depends(get_db)
):
    rc = ResourceService.update_relief_center(db, id, data)
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
    return success_response(data=resp, message="Relief center updated successfully")


# -----------------------------------------------------------------
# DASHBOARD OVERVIEW
# -----------------------------------------------------------------
@router.get("/overview", summary="Government: Master Emergency Dashboard Overview")
def get_government_overview(
    current_user: User = Depends(require_role(UserRole.GOVERNMENT)),
    db: Session = Depends(get_db)
):
    overview = DashboardService.get_government_overview(db)
    return success_response(data=overview, message="Government overview data retrieved")
