import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Text, Enum, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, generate_uuid, get_utc_now


class ShelterStatus(str, enum.Enum):
    OPEN = "OPEN"
    LIMITED = "LIMITED"
    FULL = "FULL"
    CLOSED = "CLOSED"


class Shelter(Base):
    __tablename__ = "shelters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    occupied: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[ShelterStatus] = mapped_column(
        Enum(ShelterStatus, name="shelter_status_enum", create_constraint=True),
        default=ShelterStatus.OPEN,
        nullable=False,
        index=True
    )
    is_private: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    managed_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    manager = relationship("User", foreign_keys=[managed_by])
