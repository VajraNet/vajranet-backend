from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.gateway import GatewaySyncRequest, GatewaySyncResponse
from app.services.gateway_service import GatewayService

router = APIRouter(prefix="/gateway", tags=["Offline Gateway Synchronization"])


@router.post("/sync", summary="Synchronize Offline Mesh Events", response_model=GatewaySyncResponse, status_code=status.HTTP_200_OK)
def sync_offline_events(
    sync_data: GatewaySyncRequest,
    db: Session = Depends(get_db)
):
    """
    Idempotent synchronization endpoint for offline events forwarded by gateway devices.
    
    1. Validates each event payload.
    2. Uses globally unique `message_id` for duplicate detection.
    3. Unseen events are stored, creating corresponding SOS alerts or Incidents,
       preserving the original `created_at` timestamp from the victim's device.
    4. Previously processed events are skipped and reported in `duplicates`.
    5. Returns categorized lists of `accepted`, `duplicates`, and `failed` message IDs.
    """
    response_data = GatewayService.process_offline_sync(db, sync_data)
    return response_data
