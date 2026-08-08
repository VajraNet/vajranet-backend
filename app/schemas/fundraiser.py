from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.fundraiser import FundraiserStatus


class FundraiserCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    target_amount: float = Field(..., gt=0)
    beneficiary: str = Field(..., min_length=2, max_length=255)


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
