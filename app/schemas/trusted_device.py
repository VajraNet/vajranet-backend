from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TrustedDeviceCreate(BaseModel):
    name: str = Field(..., example="Apex Emergency Control Room")
    phone: str = Field(..., example="+91 98765 43210")
    role: Optional[str] = Field("GOVERNMENT", example="GOVERNMENT")
    latitude: Optional[float] = Field(None, example=12.9716)
    longitude: Optional[float] = Field(None, example=77.5946)

class TrustedDeviceResponse(BaseModel):
    id: str
    user_id: str
    name: str
    phone: str
    role: str
    is_active: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SOSRelayRequest(BaseModel):
    raw_sms_content: str = Field(..., example="🚨 VAJRANET EMERGENCY SOS Urgency: CRITICAL GPS: 12.9716, 77.5946")
    sender_phone: Optional[str] = Field(None, example="+91 98765 00000")
    latitude: float = Field(..., example=12.9716)
    longitude: float = Field(..., example=77.5946)
    severity: Optional[str] = Field("CRITICAL", example="CRITICAL")
    user_name: Optional[str] = Field("Citizen via SMS", example="Citizen via SMS")
    notes: Optional[str] = Field(None, example="Trapped in flood water")
    relayed_by_phone: Optional[str] = Field(None, example="+91 98765 43210")
