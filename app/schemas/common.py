from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar("T")


class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")


class NearbyFilter(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="User latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="User longitude")
    radius_km: float = Field(default=15.0, gt=0, le=500.0, description="Search radius in kilometers")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int = 1
    size: int = 50
