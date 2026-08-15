from datetime import datetime
from typing import Optional, List, Union
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models.incident import IncidentType, IncidentSeverity, IncidentStatus


class IncidentCreate(BaseModel):
    title: str = Field(default="Incident Report", min_length=1, max_length=255)
    description: str = Field(default="Ground incident report", min_length=1)
    type: IncidentType = Field(default=IncidentType.OTHER)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    severity: IncidentSeverity = Field(default=IncidentSeverity.MEDIUM)
    media_urls: Optional[List[str]] = Field(default_factory=list)
    message_id: Optional[str] = None
    reported_by: Optional[str] = None


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[IncidentType] = None
    severity: Optional[IncidentSeverity] = None
    status: Optional[Union[IncidentStatus, str]] = None
    media_urls: Optional[List[str]] = None

    @field_validator('status', mode='before')
    @classmethod
    def normalize_status(cls, v):
        if not v:
            return v
        s = str(v).upper()
        if s in ['COMPLETED', 'RESOLVED']:
            return IncidentStatus.RESOLVED
        if s in ['IN_PROGRESS', 'ACCEPTED', 'DISPATCHED']:
            return IncidentStatus.IN_PROGRESS
        if s in ['VERIFIED']:
            return IncidentStatus.VERIFIED
        return IncidentStatus.REPORTED


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    message_id: Optional[str] = None
    reported_by: Optional[str] = None
    title: str
    description: str
    type: IncidentType
    latitude: float
    longitude: float
    severity: IncidentSeverity
    status: IncidentStatus
    media_urls: List[str] = []
    created_at: datetime
    updated_at: datetime
