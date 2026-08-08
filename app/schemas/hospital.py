from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.hospital import HospitalType


class HospitalCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    type: HospitalType = Field(default=HospitalType.GOVERNMENT)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    address: str = Field(..., min_length=3, max_length=500)
    emergency_available: bool = Field(default=True)
    total_beds: int = Field(default=50, ge=0)
    available_beds: int = Field(default=50, ge=0)
    icu_total: int = Field(default=10, ge=0)
    icu_available: int = Field(default=10, ge=0)


class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[HospitalType] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    address: Optional[str] = None
    emergency_available: Optional[bool] = None
    total_beds: Optional[int] = Field(None, ge=0)
    available_beds: Optional[int] = Field(None, ge=0)
    icu_total: Optional[int] = Field(None, ge=0)
    icu_available: Optional[int] = Field(None, ge=0)


class HospitalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    type: HospitalType
    latitude: float
    longitude: float
    address: str
    emergency_available: bool
    total_beds: int
    available_beds: int
    icu_total: int
    icu_available: int
    managed_by: Optional[str] = None
    distance_km: Optional[float] = None
    created_at: datetime
    updated_at: datetime
