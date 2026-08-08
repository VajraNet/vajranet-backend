from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="user or assistant")
    content: str = Field(..., description="Message text")


class AIChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="Disaster emergency question or safety query")
    history: Optional[List[ChatMessage]] = Field(default_factory=list)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)


class AIChatResponse(BaseModel):
    reply: str
    safety_advisory: str
    suggested_actions: List[str] = []
    active_announcements_count: int = 0
