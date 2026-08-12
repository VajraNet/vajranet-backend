from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class DeviceRegisterRequest(BaseModel):
    device_id: str = Field(..., min_length=3, max_length=100, description="Unique hardware/device UUID or ID")
    device_type: str = Field(default="USER_PHONE", description="RELAY, GATEWAY, or USER_PHONE")
    battery_level: Optional[int] = Field(None, ge=0, le=100)
    mesh_hop_count: int = Field(default=0, ge=0)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)


class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    device_id: str
    device_type: str
    owner_id: Optional[str] = None
    last_seen_at: datetime
    battery_level: Optional[int] = None
    mesh_hop_count: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime
