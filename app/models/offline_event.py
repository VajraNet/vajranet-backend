import enum
import json
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Text, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, generate_uuid, get_utc_now


class OfflineEventType(str, enum.Enum):
    SOS = "SOS"
    INCIDENT = "INCIDENT"
    LOCATION = "LOCATION"


class OfflineEventStatus(str, enum.Enum):
    PROCESSED = "PROCESSED"
    DUPLICATE = "DUPLICATE"
    FAILED = "FAILED"


class OfflineEvent(Base):
    __tablename__ = "offline_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    message_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    gateway_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    origin_device_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    event_type: Mapped[OfflineEventType] = mapped_column(
        Enum(OfflineEventType, name="offline_event_type_enum", create_constraint=True),
        nullable=False,
        index=True
    )
    _payload: Mapped[str] = mapped_column("payload", Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)
    status: Mapped[OfflineEventStatus] = mapped_column(
        Enum(OfflineEventStatus, name="offline_event_status_enum", create_constraint=True),
        default=OfflineEventStatus.PROCESSED,
        nullable=False,
        index=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    @property
    def payload(self) -> Dict[str, Any]:
        try:
            return json.loads(self._payload)
        except Exception:
            return {}

    @payload.setter
    def payload(self, data: Dict[str, Any]) -> None:
        self._payload = json.dumps(data or {})
