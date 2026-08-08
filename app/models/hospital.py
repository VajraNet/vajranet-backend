import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Enum, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, generate_uuid, get_utc_now


class HospitalType(str, enum.Enum):
    GOVERNMENT = "GOVERNMENT"
    PRIVATE = "PRIVATE"


class Hospital(Base):
    __tablename__ = "hospitals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[HospitalType] = mapped_column(
        Enum(HospitalType, name="hospital_type_enum", create_constraint=True),
        default=HospitalType.GOVERNMENT,
        nullable=False,
        index=True
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    emergency_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    total_beds: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    available_beds: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    icu_total: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    icu_available: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    managed_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    manager = relationship("User", foreign_keys=[managed_by])
