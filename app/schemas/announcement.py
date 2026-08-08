from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.announcement import AnnouncementType, AnnouncementPriority


class AnnouncementCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    content: str = Field(..., min_length=5)
    type: AnnouncementType = Field(default=AnnouncementType.ALERT)
    area: Optional[str] = Field(None, max_length=255)
    priority: AnnouncementPriority = Field(default=AnnouncementPriority.HIGH)
    expires_at: Optional[datetime] = None


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    type: Optional[AnnouncementType] = None
    area: Optional[str] = None
    priority: Optional[AnnouncementPriority] = None
    expires_at: Optional[datetime] = None


class AnnouncementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    content: str
    type: AnnouncementType
    area: Optional[str] = None
    priority: AnnouncementPriority
    created_by: str
    created_at: datetime
    expires_at: Optional[datetime] = None
