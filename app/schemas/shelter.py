from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.shelter import ShelterStatus


class ShelterCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    address: str = Field(..., min_length=3, max_length=500)
    capacity: int = Field(default=100, gt=0)
    occupied: int = Field(default=0, ge=0)
    status: ShelterStatus = Field(default=ShelterStatus.OPEN)
    is_private: bool = Field(default=False)


class ShelterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    address: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)
    occupied: Optional[int] = Field(None, ge=0)
    status: Optional[ShelterStatus] = None


class ShelterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    address: str
    capacity: int
    occupied: int
    available_capacity: Optional[int] = None
    status: ShelterStatus
    is_private: bool
    managed_by: Optional[str] = None
    distance_km: Optional[float] = None
    created_at: datetime
    updated_at: datetime
