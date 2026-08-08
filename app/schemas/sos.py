from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.sos import SOSSeverity, SOSStatus


class SOSCreate(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="Description of the emergency situation")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude of victim")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude of victim")
    severity: SOSSeverity = Field(default=SOSSeverity.CRITICAL, description="Severity level")
    message_id: Optional[str] = Field(None, description="Optional custom or offline-assigned message identifier")
    origin_device_id: Optional[str] = Field(None, description="Originating device ID if known")


class SOSUpdate(BaseModel):
    status: Optional[SOSStatus] = None
    severity: Optional[SOSSeverity] = None


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
