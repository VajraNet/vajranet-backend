from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.announcement import Announcement, AnnouncementPriority, AnnouncementType
from app.models.user import User
from app.schemas.announcement import AnnouncementCreate, AnnouncementUpdate
from app.models.base import get_utc_now


class AnnouncementService:
    @staticmethod
    def create_announcement(db: Session, data: AnnouncementCreate, author: User) -> Announcement:
        announcement = Announcement(
            title=data.title,
            content=data.content,
            type=data.type,
            area=data.area,
            priority=data.priority,
            created_by=author.id,
            created_at=get_utc_now(),
            expires_at=data.expires_at,
        )
        db.add(announcement)
        db.commit()
        db.refresh(announcement)
        return announcement

    @staticmethod
    def update_announcement(db: Session, announcement_id: str, data: AnnouncementUpdate) -> Optional[Announcement]:
        announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
        if not announcement:
            return None

        if data.title is not None:
            announcement.title = data.title
        if data.content is not None:
            announcement.content = data.content
        if data.type is not None:
            announcement.type = data.type
        if data.area is not None:
            announcement.area = data.area
        if data.priority is not None:
            announcement.priority = data.priority
        if data.expires_at is not None:
            announcement.expires_at = data.expires_at

        db.commit()
        db.refresh(announcement)
        return announcement

    @staticmethod
    def get_announcement_by_id(db: Session, announcement_id: str) -> Optional[Announcement]:
        return db.query(Announcement).filter(Announcement.id == announcement_id).first()

    @staticmethod
    def get_active_announcements(db: Session) -> List[Announcement]:
        now = get_utc_now()
        query = db.query(Announcement).filter(
            (Announcement.expires_at.is_(None)) | (Announcement.expires_at > now)
        )
        # Sort critical/high first, then latest
        return query.order_by(
            Announcement.created_at.desc()
        ).all()

    @staticmethod
    def get_all_announcements(db: Session, skip: int = 0, limit: int = 100) -> List[Announcement]:
        return db.query(Announcement).order_by(Announcement.created_at.desc()).offset(skip).limit(limit).all()
