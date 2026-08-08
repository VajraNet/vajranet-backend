from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.volunteer import VolunteerAvailability, TaskStatus


class VolunteerProfileCreate(BaseModel):
    skills: List[str] = Field(default_factory=lambda: ["First Aid", "Search & Rescue", "Logistics"])
    availability_status: VolunteerAvailability = Field(default=VolunteerAvailability.AVAILABLE)
    phone: Optional[str] = None
    location: Optional[str] = None


class VolunteerProfileUpdate(BaseModel):
    skills: Optional[List[str]] = None
    availability_status: Optional[VolunteerAvailability] = None
    phone: Optional[str] = None
    location: Optional[str] = None


class VolunteerProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    skills: List[str] = []
    availability_status: VolunteerAvailability
    phone: Optional[str] = None
    location: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class VolunteerTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    incident_id: str
    volunteer_id: str
    status: TaskStatus
    notes: Optional[str] = None
    assigned_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class TaskStatusUpdate(BaseModel):
    status: TaskStatus
    notes: Optional[str] = None
