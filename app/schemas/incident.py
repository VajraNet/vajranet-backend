from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models.incident import IncidentType, IncidentSeverity, IncidentStatus


class IncidentCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    type: IncidentType = Field(default=IncidentType.OTHER)
    latitude: float = Field(default=28.6139, ge=-90.0, le=90.0)
    longitude: float = Field(default=77.2090, ge=-180.0, le=180.0)
    severity: IncidentSeverity = Field(default=IncidentSeverity.MEDIUM)
    media_urls: Optional[List[str]] = Field(default_factory=list)
    message_id: Optional[str] = None

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, v: Any) -> Any:
        if isinstance(v, str):
            clean = v.strip().upper().replace(" ", "_")
            if clean in IncidentType.__members__:
                return IncidentType[clean]
            if "MEDICAL" in clean:
                return IncidentType.MEDICAL
            if "BUILDING" in clean or "COLLAPSE" in clean:
                return IncidentType.BUILDING_COLLAPSE
            return IncidentType.OTHER
        return v

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_severity(cls, v: Any) -> Any:
        if isinstance(v, str):
            clean = v.strip().upper()
            if clean in IncidentSeverity.__members__:
                return IncidentSeverity[clean]
            return IncidentSeverity.MEDIUM
        return v


class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[IncidentType] = None
    severity: Optional[IncidentSeverity] = None
    status: Optional[IncidentStatus] = None
    media_urls: Optional[List[str]] = None

    @field_validator("type", mode="before")
    @classmethod
    def normalize_update_type(cls, v: Any) -> Any:
        if isinstance(v, str):
            clean = v.strip().upper().replace(" ", "_")
            if clean in IncidentType.__members__:
                return IncidentType[clean]
            return IncidentType.OTHER
        return v


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
