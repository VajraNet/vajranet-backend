import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, generate_uuid, get_utc_now


class SOSSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SOSStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"


class SOSAlert(Base):
    __tablename__ = "sos_alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    message_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    citizen_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    origin_device_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    severity: Mapped[SOSSeverity] = mapped_column(
        Enum(SOSSeverity, name="sos_severity_enum", create_constraint=True),
        default=SOSSeverity.CRITICAL,
        nullable=False,
        index=True
    )
    status: Mapped[SOSStatus] = mapped_column(
        Enum(SOSStatus, name="sos_status_enum", create_constraint=True),
        default=SOSStatus.ACTIVE,
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False, index=True)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    citizen = relationship("User", back_populates="sos_alerts", foreign_keys=[citizen_id])
