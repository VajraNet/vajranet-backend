from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class TrustedDeviceCreate(BaseModel):
    name: str = Field(..., description="Device or team name")
    phone: str = Field(..., description="Phone number")
    role: Optional[str] = Field("GOVERNMENT", description="Role of device/operator")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")

class TrustedDeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    name: str
    phone: str
    role: str
    is_active: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: Optional[datetime] = None

class SOSRelayRequest(BaseModel):
    raw_sms_content: str = Field(..., description="Raw SMS content received")
    sender_phone: Optional[str] = Field(None, description="Sender phone number")
    latitude: float = Field(..., description="Victim latitude")
    longitude: float = Field(..., description="Victim longitude")
    severity: Optional[str] = Field("CRITICAL", description="Severity level")
    user_name: Optional[str] = Field("Citizen via SMS", description="Victim name")
    notes: Optional[str] = Field(None, description="Additional notes")
    relayed_by_phone: Optional[str] = Field(None, description="Relaying trusted phone")
