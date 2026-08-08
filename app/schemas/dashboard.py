from typing import Optional, List
from pydantic import BaseModel
from app.schemas.sos import SOSResponse
from app.schemas.incident import IncidentResponse
from app.schemas.announcement import AnnouncementResponse
from app.schemas.shelter import ShelterResponse
from app.schemas.hospital import HospitalResponse
from app.schemas.volunteer import VolunteerTaskResponse


class CitizenOverviewResponse(BaseModel):
    active_sos: Optional[SOSResponse] = None
    total_my_incidents: int = 0
    my_incidents: List[IncidentResponse] = []
    nearby_shelters_count: int = 0
    nearby_hospitals_count: int = 0
    active_announcements: List[AnnouncementResponse] = []


class GovernmentOverviewResponse(BaseModel):
    active_sos_count: int = 0
    active_incidents_count: int = 0
    critical_incidents_count: int = 0
    volunteers_responding_count: int = 0
    available_shelters_count: int = 0
    total_shelter_capacity: int = 0
    total_shelter_occupied: int = 0
    available_hospital_beds: int = 0
    available_icu_beds: int = 0
    active_announcements_count: int = 0
    recent_incidents: List[IncidentResponse] = []
    recent_sos: List[SOSResponse] = []


class VolunteerOverviewResponse(BaseModel):
    available_tasks_count: int = 0
    accepted_tasks_count: int = 0
    active_tasks_count: int = 0
    completed_tasks_count: int = 0
    my_active_tasks: List[VolunteerTaskResponse] = []
    nearby_incidents_count: int = 0
    active_fundraisers_count: int = 0
    volunteer_status: str = "AVAILABLE"
