from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, generate_uuid, get_utc_now


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    device_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    device_type: Mapped[str] = mapped_column(String(50), default="USER_PHONE", nullable=False)
    owner_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)
    battery_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mesh_hop_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)

    owner = relationship("User", foreign_keys=[owner_id])
