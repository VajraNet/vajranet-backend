from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.models.offline_event import OfflineEventType


class GatewayEventItem(BaseModel):
    message_id: str = Field(..., min_length=3, max_length=100, description="Globally unique message identifier")
    type: OfflineEventType = Field(..., description="Type of event: SOS, INCIDENT, or LOCATION")
    created_at: datetime = Field(..., description="Original timestamp recorded by victim device")
    origin_device_id: Optional[str] = Field(None, description="Originating device identifier")
    payload: Dict[str, Any] = Field(..., description="Payload containing event-specific parameters")


class GatewaySyncRequest(BaseModel):
    gateway_id: str = Field(..., min_length=2, max_length=100, description="Identifier of the gateway forwarding offline events")
    events: List[GatewayEventItem] = Field(..., min_length=1, description="List of offline events to synchronize")


class GatewaySyncResponse(BaseModel):
    success: bool = True
    accepted: List[str] = Field(default_factory=list, description="List of newly processed message_ids")
    duplicates: List[str] = Field(default_factory=list, description="List of message_ids previously processed")
    failed: List[str] = Field(default_factory=list, description="List of message_ids that failed validation or processing")
