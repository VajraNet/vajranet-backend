import enum
import json
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Float, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, generate_uuid, get_utc_now


class ReliefCenterStatus(str, enum.Enum):
    OPEN = "OPEN"
    LIMITED = "LIMITED"
    CLOSED = "CLOSED"


class ReliefCenter(Base):
    __tablename__ = "relief_centers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    _items_available: Mapped[str] = mapped_column("items_available", Text, default="[]", nullable=False)
    status: Mapped[ReliefCenterStatus] = mapped_column(
        Enum(ReliefCenterStatus, name="relief_center_status_enum", create_constraint=True),
        default=ReliefCenterStatus.OPEN,
        nullable=False,
        index=True
    )
    managed_by: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    manager = relationship("User", foreign_keys=[managed_by])

    @property
    def items_available(self) -> List[str]:
        try:
            return json.loads(self._items_available)
        except Exception:
            return []

    @items_available.setter
    def items_available(self, items: List[str]) -> None:
        self._items_available = json.dumps(items or [])
