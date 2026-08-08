from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.relief_center import ReliefCenterStatus


class ReliefCenterCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    address: str = Field(..., min_length=3, max_length=500)
    items_available: List[str] = Field(default_factory=lambda: ["Food", "Water", "Medicine", "Clothing"])
    status: ReliefCenterStatus = Field(default=ReliefCenterStatus.OPEN)


class ReliefCenterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    address: Optional[str] = None
    items_available: Optional[List[str]] = None
    status: Optional[ReliefCenterStatus] = None


class ReliefCenterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    address: str
    items_available: List[str] = []
    status: ReliefCenterStatus
    managed_by: Optional[str] = None
    distance_km: Optional[float] = None
    created_at: datetime
    updated_at: datetime
