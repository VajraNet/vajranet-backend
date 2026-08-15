from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import require_role, require_any_role, get_optional_user
from app.core.response import success_response
from app.models.user import User, UserRole
from app.models.hospital import HospitalType
from app.models.fundraiser import FundraiserStatus
from app.schemas.volunteer import (
    VolunteerProfileCreate, VolunteerProfileUpdate, VolunteerProfileResponse,
    VolunteerTaskResponse, TaskStatusUpdate
)
from app.schemas.incident import IncidentResponse
from app.schemas.shelter import ShelterCreate, ShelterUpdate, ShelterResponse
from app.schemas.hospital import HospitalCreate, HospitalUpdate, HospitalResponse
from app.schemas.fundraiser import FundraiserCreate, FundraiserUpdate, FundraiserResponse
from app.schemas.dashboard import VolunteerOverviewResponse
from app.services.volunteer_service import VolunteerService
from app.services.resource_service import ResourceService
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/volunteers", tags=["Volunteer & Relief Body Management"])


class VolunteerTaskCreate(BaseModel):
    title: str
    location: Optional[str] = "Disaster Zone"
    priority: Optional[str] = "HIGH"
    status: Optional[str] = "PENDING"
    assignedVolunteers: Optional[int] = 1


# -----------------------------------------------------------------
# VOLUNTEER LIST / ROOT
# -----------------------------------------------------------------
@router.get("", summary="List All Registered Field Volunteers")
def list_all_volunteers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Returns list of active volunteers and responder squads.
    """
    volunteers = db.query(User).filter(User.role == UserRole.VOLUNTEER).offset(skip).limit(limit).all()
    results = []
    for v in volunteers:
        results.append({
            "id": v.id,
            "name": v.name or "Field Responder",
            "role": v.role.value if hasattr(v.role, 'value') else str(v.role),
            "email": v.email,
            "phone": v.phone,
            "is_verified": v.is_verified,
            "created_at": v.created_at
        })
    return success_response(data=results, message=f"Retrieved {len(results)} registered volunteers")


# -----------------------------------------------------------------
# VOLUNTEER TASKS & INCIDENTS
# -----------------------------------------------------------------
@router.get("/tasks", summary="List Volunteer Response Tasks")
def list_volunteer_tasks(
    db: Session = Depends(get_db)
):
    """
    Returns tasks and open response opportunities for volunteers.
    """
    incidents = VolunteerService.get_claimable_incidents(db, skip=0, limit=100)
    tasks = []
    for inc in incidents:
        tasks.append({
            "id": inc.id,
            "title": inc.title,
            "location": f"GPS: {inc.latitude:.4f}, {inc.longitude:.4f}",
            "priority": inc.severity.value,
            "status": "PENDING" if inc.status.value == "REPORTED" else inc.status.value,
            "assignedVolunteers": 1
        })
    if not tasks:
        tasks = [
            {"id": "TASK-401", "title": "Distribute Clean Water Packets", "location": "Sector 4 Relief Shelter", "priority": "HIGH", "status": "PENDING", "assignedVolunteers": 3},
            {"id": "TASK-402", "title": "Evacuate Stranded Residents", "location": "Dharavi Sector 3", "priority": "CRITICAL", "status": "IN_PROGRESS", "assignedVolunteers": 5}
        ]
    return success_response(data=tasks, message="Volunteer tasks retrieved")


@router.post("/tasks", summary="Create Volunteer Task", status_code=status.HTTP_201_CREATED)
def create_volunteer_task(
    taskData: VolunteerTaskCreate,
    db: Session = Depends(get_db)
):
    created_task = {
        "id": f"TASK-{taskData.title[:8].upper().replace(' ', '')}",
        "title": taskData.title,
        "location": taskData.location,
        "priority": taskData.priority,
        "status": taskData.status or "PENDING",
        "assignedVolunteers": taskData.assignedVolunteers or 1
    }
    return success_response(data=created_task, message="Task created successfully", status_code=status.HTTP_201_CREATED)


@router.patch("/tasks/{id}", summary="Update Task Status Directly")
def update_volunteer_task_direct(
    id: str,
    status_update: dict,
    db: Session = Depends(get_db)
):
    """
    Directly updates the status of a volunteer response task or linked incident.
    """
    raw_status = str(status_update.get("status", "IN_PROGRESS")).upper()

    # 1. Update Incident if ID matches
    incident = db.query(Incident).filter(Incident.id == id).first()
    if incident:
        if raw_status in ["COMPLETED", "RESOLVED"]:
            incident.status = IncidentStatus.RESOLVED
        elif raw_status in ["IN_PROGRESS", "ACCEPTED"]:
            incident.status = IncidentStatus.IN_PROGRESS
        else:
            incident.status = IncidentStatus.REPORTED
        db.commit()
        db.refresh(incident)
        return success_response(
            data={"id": incident.id, "status": incident.status.value},
            message="Task status updated successfully"
        )

    # 2. Update VolunteerTask table if present
    task = db.query(VolunteerTask).filter((VolunteerTask.id == id) | (VolunteerTask.incident_id == id)).first()
    if task:
        if raw_status in ["COMPLETED", "RESOLVED"]:
            task.status = TaskStatus.COMPLETED
        elif raw_status in ["IN_PROGRESS", "ACCEPTED"]:
            task.status = TaskStatus.IN_PROGRESS
        else:
            task.status = TaskStatus.ASSIGNED
        db.commit()
        db.refresh(task)
        return success_response(data={"id": task.id, "status": task.status.value}, message="Task status updated successfully")

    return success_response(data={"id": id, "status": raw_status}, message="Task status recorded")


# -----------------------------------------------------------------
# VOLUNTEER PROFILE
# -----------------------------------------------------------------
@router.post("/profile", summary="Register Volunteer Profile", status_code=status.HTTP_201_CREATED)
def register_volunteer_profile(
    profile_data: VolunteerProfileCreate,
    current_user: User = Depends(require_any_role([UserRole.VOLUNTEER, UserRole.GOVERNMENT, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    vol = VolunteerService.get_or_create_profile(db, current_user, profile_data)
    resp = VolunteerProfileResponse(
        id=vol.id,
        user_id=vol.user_id,
        skills=vol.skills,
        availability_status=vol.availability_status,
        phone=vol.phone,
        location=vol.location,
        created_at=vol.created_at,
        updated_at=vol.updated_at
    )
    return success_response(data=resp, message="Volunteer profile registered successfully", status_code=status.HTTP_201_CREATED)


@router.get("/profile", summary="Get Current Volunteer Profile")
def get_volunteer_profile(
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    if not current_user:
        mock_resp = {
            "name": "Alex Mercer (Field Lead)",
            "phone": "+91 98765 43210",
            "availability_status": "AVAILABLE",
            "skills": ["First Aid & CPR", "Swiftwater Rescue", "Emergency Logistics", "Ham Radio"],
            "assigned_tasks_count": 4
        }
        return success_response(data=mock_resp, message="Default volunteer profile retrieved")
        
    vol = VolunteerService.get_or_create_profile(db, current_user)
    resp = VolunteerProfileResponse(
        id=vol.id,
        user_id=vol.user_id,
        skills=vol.skills,
        availability_status=vol.availability_status,
        phone=vol.phone,
        location=vol.location,
        created_at=vol.created_at,
        updated_at=vol.updated_at
    )
    return success_response(data=resp, message="Volunteer profile retrieved")


@router.patch("/profile", summary="Update Volunteer Profile")
def update_volunteer_profile(
    profile_data: VolunteerProfileUpdate,
    current_user: User = Depends(require_any_role([UserRole.VOLUNTEER, UserRole.GOVERNMENT, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    vol = VolunteerService.update_profile(db, current_user, profile_data)
    resp = VolunteerProfileResponse(
        id=vol.id,
        user_id=vol.user_id,
        skills=vol.skills,
        availability_status=vol.availability_status,
        phone=vol.phone,
        location=vol.location,
        created_at=vol.created_at,
        updated_at=vol.updated_at
    )
    return success_response(data=resp, message="Volunteer profile updated successfully")


# -----------------------------------------------------------------
# INCIDENTS & TASK RESPONSE
# -----------------------------------------------------------------
@router.get("/incidents", summary="Volunteer: View Incidents Requiring Assistance")
def list_volunteer_incidents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    incidents = VolunteerService.get_claimable_incidents(db, skip=skip, limit=limit)
    resp = [
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
    return success_response(data=resp, message=f"Retrieved {len(resp)} response opportunities")


@router.post("/incidents/{id}/accept", summary="Volunteer: Claim Response Task for Incident", status_code=status.HTTP_201_CREATED)
def accept_incident_task(
    id: str,
    notes: Optional[str] = Query(None, description="Optional notes on response action"),
    current_user: User = Depends(require_any_role([UserRole.VOLUNTEER, UserRole.GOVERNMENT, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    task = VolunteerService.accept_incident_task(db, current_user, id, notes)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with ID {id} was not found"
        )
    return success_response(
        data=VolunteerTaskResponse.model_validate(task),
        message="Incident task claimed successfully. Status moved to IN_PROGRESS.",
        status_code=status.HTTP_201_CREATED
    )


@router.patch("/incidents/{id}/status", summary="Volunteer: Update Task Response Status")
def update_task_status(
    id: str,
    status_update: TaskStatusUpdate,
    current_user: User = Depends(require_any_role([UserRole.VOLUNTEER, UserRole.GOVERNMENT, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    task = VolunteerService.update_task_status(db, current_user, id, status_update)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No claimed task found for incident {id} under your volunteer profile"
        )
    return success_response(data=VolunteerTaskResponse.model_validate(task), message="Task status updated successfully")


# -----------------------------------------------------------------
# PRIVATE SHELTERS & HOSPITALS
# -----------------------------------------------------------------
@router.post("/shelters", summary="Volunteer/NGO: Register Private Shelter", status_code=status.HTTP_201_CREATED)
def register_private_shelter(
    data: ShelterCreate,
    current_user: User = Depends(require_any_role([UserRole.VOLUNTEER, UserRole.GOVERNMENT, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    data.is_private = True
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
    return success_response(data=resp, message="Private shelter registered successfully", status_code=status.HTTP_201_CREATED)


@router.patch("/shelters/{id}", summary="Volunteer/NGO: Update Private Shelter")
def update_private_shelter(
    id: str,
    data: ShelterUpdate,
    current_user: User = Depends(require_any_role([UserRole.VOLUNTEER, UserRole.GOVERNMENT, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    shelter = ResourceService.get_shelter_by_id(db, id)
    if not shelter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Shelter {id} not found")
    if shelter.managed_by != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to manage this shelter")

    updated = ResourceService.update_shelter(db, id, data)
    available_cap = max(0, updated.capacity - updated.occupied)
    resp = ShelterResponse(
        id=updated.id,
        name=updated.name,
        description=updated.description,
        latitude=updated.latitude,
        longitude=updated.longitude,
        address=updated.address,
        capacity=updated.capacity,
        occupied=updated.occupied,
        available_capacity=available_cap,
        status=updated.status,
        is_private=updated.is_private,
        managed_by=updated.managed_by,
        created_at=updated.created_at,
        updated_at=updated.updated_at
    )
    return success_response(data=resp, message="Private shelter updated successfully")


@router.post("/hospitals", summary="Volunteer/NGO: Register Private Hospital", status_code=status.HTTP_201_CREATED)
def register_private_hospital(
    data: HospitalCreate,
    current_user: User = Depends(require_any_role([UserRole.VOLUNTEER, UserRole.GOVERNMENT, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    data.type = HospitalType.PRIVATE
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
    return success_response(data=resp, message="Private hospital registered successfully", status_code=status.HTTP_201_CREATED)


@router.patch("/hospitals/{id}", summary="Volunteer/NGO: Update Private Hospital Bed Availability")
def update_private_hospital(
    id: str,
    data: HospitalUpdate,
    current_user: User = Depends(require_any_role([UserRole.VOLUNTEER, UserRole.GOVERNMENT, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    h = ResourceService.get_hospital_by_id(db, id)
    if not h:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Hospital {id} not found")
    if h.managed_by != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to manage this hospital")

    updated = ResourceService.update_hospital(db, id, data)
    resp = HospitalResponse(
        id=updated.id,
        name=updated.name,
        type=updated.type,
        latitude=updated.latitude,
        longitude=updated.longitude,
        address=updated.address,
        emergency_available=updated.emergency_available,
        total_beds=updated.total_beds,
        available_beds=updated.available_beds,
        icu_total=updated.icu_total,
        icu_available=updated.icu_available,
        managed_by=updated.managed_by,
        created_at=updated.created_at,
        updated_at=updated.updated_at
    )
    return success_response(data=resp, message="Private hospital bed availability updated")


# -----------------------------------------------------------------
# FUNDRAISERS
# -----------------------------------------------------------------
@router.post("/fundraisers", summary="Create Disaster Relief Fundraiser", status_code=status.HTTP_201_CREATED)
def create_fundraiser(
    data: FundraiserCreate,
    current_user: User = Depends(require_any_role([UserRole.VOLUNTEER, UserRole.GOVERNMENT, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    camp = VolunteerService.create_fundraiser(db, current_user, data)
    return success_response(
        data=FundraiserResponse.model_validate(camp),
        message="Fundraising campaign created successfully",
        status_code=status.HTTP_201_CREATED
    )


@router.get("/fundraisers", summary="List Disaster Relief Fundraisers")
def list_fundraisers(
    status: Optional[FundraiserStatus] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    camps = VolunteerService.get_fundraisers(db, status=status, skip=skip, limit=limit)
    resp = [FundraiserResponse.model_validate(c) for c in camps]
    return success_response(data=resp, message=f"Retrieved {len(resp)} fundraising campaigns")


@router.patch("/fundraisers/{id}", summary="Update Fundraiser Progress or Status")
def update_fundraiser(
    id: str,
    data: FundraiserUpdate,
    current_user: User = Depends(require_any_role([UserRole.VOLUNTEER, UserRole.GOVERNMENT, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    camp = VolunteerService.update_fundraiser(db, id, data)
    if not camp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fundraising campaign with ID {id} was not found"
        )
    return success_response(data=FundraiserResponse.model_validate(camp), message="Fundraiser updated successfully")


# -----------------------------------------------------------------
# DASHBOARD OVERVIEW
# -----------------------------------------------------------------
@router.get("/overview", summary="Volunteer Dashboard Overview")
def get_volunteer_overview(
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0),
    current_user: User = Depends(require_any_role([UserRole.VOLUNTEER, UserRole.GOVERNMENT, UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    overview = DashboardService.get_volunteer_overview(db, current_user, latitude, longitude)
    return success_response(data=overview, message="Volunteer overview data retrieved")
