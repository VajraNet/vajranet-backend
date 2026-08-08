from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.response import success_response
from app.schemas.announcement import AnnouncementResponse
from app.services.announcement_service import AnnouncementService

router = APIRouter(prefix="/announcements", tags=["Emergency Announcements"])


@router.get("", summary="Get Active Emergency Announcements")
def get_active_announcements(db: Session = Depends(get_db)):
    """
    Returns all active official government emergency broadcasts,
    safety instructions, and evacuation advisories ordered by priority.
    """
    announcements = AnnouncementService.get_active_announcements(db)
    response_data = [AnnouncementResponse.model_validate(a) for a in announcements]
    return success_response(data=response_data, message="Active announcements retrieved")
