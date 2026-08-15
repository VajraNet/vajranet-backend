from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_optional_user
from app.core.response import success_response
from app.models.user import User
from app.schemas.announcement import AnnouncementCreate, AnnouncementResponse
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


@router.post("", summary="Publish Emergency Announcement", status_code=status.HTTP_201_CREATED)
def publish_announcement(
    data: AnnouncementCreate,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Broadcasts a new emergency bulletin or evacuation advisory directly into the database.
    """
    anc = AnnouncementService.create_announcement(db, data, current_user)
    return success_response(
        data=AnnouncementResponse.model_validate(anc),
        message="Emergency announcement broadcasted successfully",
        status_code=status.HTTP_201_CREATED
    )
