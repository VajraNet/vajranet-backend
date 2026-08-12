from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class EmergencyContactBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=1, max_length=20)
    relation: Optional[str] = Field(None, max_length=50)

class EmergencyContactCreate(EmergencyContactBase):
    pass

class EmergencyContactUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=1, max_length=20)
    relation: Optional[str] = Field(None, max_length=50)

class EmergencyContactResponse(EmergencyContactBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
