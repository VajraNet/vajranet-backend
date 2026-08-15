from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.fundraiser import FundraiserStatus


class FundraiserCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(default="Emergency disaster relief fund", min_length=1)
    target_amount: float = Field(default=50000.0, gt=0)
    beneficiary: Optional[str] = Field(default="Disaster Relief Victims", min_length=1, max_length=255)
    raised_amount: Optional[float] = Field(default=0.0, ge=0)


class FundraiserUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_amount: Optional[float] = Field(None, gt=0)
    raised_amount: Optional[float] = Field(None, ge=0)
    beneficiary: Optional[str] = None
    status: Optional[FundraiserStatus] = None


class FundraiserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    target_amount: float
    raised_amount: float
    beneficiary: str
    status: FundraiserStatus
    created_by: str
    created_at: datetime
    updated_at: datetime
