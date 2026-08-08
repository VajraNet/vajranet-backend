from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models.sos import SOSSeverity, SOSStatus


class SOSCreate(BaseModel):
    message: Optional[str] = Field(default="Immediate emergency assistance requested", max_length=1000, description="Description of the emergency situation")
    latitude: Optional[float] = Field(default=28.6139, ge=-90.0, le=90.0, description="Latitude of victim")
    longitude: Optional[float] = Field(default=77.2090, ge=-180.0, le=180.0, description="Longitude of victim")
    severity: SOSSeverity = Field(default=SOSSeverity.CRITICAL, description="Severity level")
    message_id: Optional[str] = Field(None, description="Optional custom or offline-assigned message identifier")
    origin_device_id: Optional[str] = Field(None, description="Originating device ID if known")
    locationName: Optional[str] = Field(None, description="Optional textual location name")

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_sos_severity(cls, v: Any) -> Any:
        if isinstance(v, str):
            clean = v.strip().upper()
            if clean in SOSSeverity.__members__:
                return SOSSeverity[clean]
            return SOSSeverity.CRITICAL
        return v


class SOSUpdate(BaseModel):
    status: Optional[SOSStatus] = None
    severity: Optional[SOSSeverity] = None

    @field_validator("severity", mode="before")
    @classmethod
    def normalize_sos_update_severity(cls, v: Any) -> Any:
        if isinstance(v, str):
            clean = v.strip().upper()
            if clean in SOSSeverity.__members__:
                return SOSSeverity[clean]
        return v


class SOSResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    message_id: str
    citizen_id: Optional[str] = None
    origin_device_id: Optional[str] = None
    message: str
    latitude: float
    longitude: float
    severity: SOSSeverity
    status: SOSStatus
    created_at: datetime
    received_at: datetime
    resolved_at: Optional[datetime] = None
