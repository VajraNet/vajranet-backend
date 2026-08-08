import enum
import json
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, generate_uuid, get_utc_now


class VolunteerAvailability(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"


class TaskStatus(str, enum.Enum):
    ASSIGNED = "ASSIGNED"
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Volunteer(Base):
    __tablename__ = "volunteers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), unique=True, nullable=False, index=True)
    _skills: Mapped[str] = mapped_column("skills", Text, default="[]", nullable=False)
    availability_status: Mapped[VolunteerAvailability] = mapped_column(
        Enum(VolunteerAvailability, name="volunteer_availability_enum", create_constraint=True),
        default=VolunteerAvailability.AVAILABLE,
        nullable=False,
        index=True
    )
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="volunteer_profile", foreign_keys=[user_id])
    tasks = relationship("VolunteerTask", back_populates="volunteer", cascade="all, delete-orphan")

    @property
    def skills(self) -> List[str]:
        try:
            return json.loads(self._skills)
        except Exception:
            return []

    @skills.setter
    def skills(self, skill_list: List[str]) -> None:
        self._skills = json.dumps(skill_list or [])


class VolunteerTask(Base):
    __tablename__ = "volunteer_tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    incident_id: Mapped[str] = mapped_column(String(36), ForeignKey("incidents.id"), nullable=False, index=True)
    volunteer_id: Mapped[str] = mapped_column(String(36), ForeignKey("volunteers.id"), nullable=False, index=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status_enum", create_constraint=True),
        default=TaskStatus.ACCEPTED,
        nullable=False,
        index=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    incident = relationship("Incident", back_populates="tasks", foreign_keys=[incident_id])
    volunteer = relationship("Volunteer", back_populates="tasks", foreign_keys=[volunteer_id])
