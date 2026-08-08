import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, generate_uuid, get_utc_now


class AnnouncementType(str, enum.Enum):
    ALERT = "ALERT"
    SAFETY_INSTRUCTION = "SAFETY_INSTRUCTION"
    EVACUATION = "EVACUATION"
    INCIDENT_UPDATE = "INCIDENT_UPDATE"
    SHELTER_INFO = "SHELTER_INFO"
    GENERAL_UPDATE = "GENERAL_UPDATE"


class AnnouncementPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[AnnouncementType] = mapped_column(
        Enum(AnnouncementType, name="announcement_type_enum", create_constraint=True),
        default=AnnouncementType.ALERT,
        nullable=False,
        index=True
    )
    area: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    priority: Mapped[AnnouncementPriority] = mapped_column(
        Enum(AnnouncementPriority, name="announcement_priority_enum", create_constraint=True),
        default=AnnouncementPriority.HIGH,
        nullable=False,
        index=True
    )
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False, index=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    author = relationship("User", foreign_keys=[created_by])
