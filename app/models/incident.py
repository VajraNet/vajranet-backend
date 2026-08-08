import enum
import json
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Float, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, generate_uuid, get_utc_now


class IncidentType(str, enum.Enum):
    FLOOD = "FLOOD"
    EARTHQUAKE = "EARTHQUAKE"
    FIRE = "FIRE"
    LANDSLIDE = "LANDSLIDE"
    ACCIDENT = "ACCIDENT"
    BUILDING_COLLAPSE = "BUILDING_COLLAPSE"
    MEDICAL = "MEDICAL"
    OTHER = "OTHER"


class IncidentSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentStatus(str, enum.Enum):
    REPORTED = "REPORTED"
    VERIFIED = "VERIFIED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    message_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True, nullable=True)
    reported_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[IncidentType] = mapped_column(
        Enum(IncidentType, name="incident_type_enum", create_constraint=True),
        default=IncidentType.OTHER,
        nullable=False,
        index=True
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity, name="incident_severity_enum", create_constraint=True),
        default=IncidentSeverity.MEDIUM,
        nullable=False,
        index=True
    )
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus, name="incident_status_enum", create_constraint=True),
        default=IncidentStatus.REPORTED,
        nullable=False,
        index=True
    )
    _media_urls: Mapped[str] = mapped_column("media_urls", Text, default="[]", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    # Relationships
    reporter = relationship("User", back_populates="incidents", foreign_keys=[reported_by])
    tasks = relationship("VolunteerTask", back_populates="incident", cascade="all, delete-orphan")

    @property
    def media_urls(self) -> List[str]:
        try:
            return json.loads(self._media_urls)
        except Exception:
            return []

    @media_urls.setter
    def media_urls(self, urls: List[str]) -> None:
        self._media_urls = json.dumps(urls or [])
