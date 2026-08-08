import enum
from datetime import datetime
from sqlalchemy import String, Text, Enum, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, generate_uuid, get_utc_now


class FundraiserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"


class FundraisingCampaign(Base):
    __tablename__ = "fundraising_campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    target_amount: Mapped[float] = mapped_column(Float, nullable=False)
    raised_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    beneficiary: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[FundraiserStatus] = mapped_column(
        Enum(FundraiserStatus, name="fundraiser_status_enum", create_constraint=True),
        default=FundraiserStatus.ACTIVE,
        nullable=False,
        index=True
    )
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=get_utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False
    )

    creator = relationship("User", foreign_keys=[created_by])
