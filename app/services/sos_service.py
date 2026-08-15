import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.sos import SOSAlert, SOSStatus, SOSSeverity
from app.models.user import User
from app.schemas.sos import SOSCreate, SOSUpdate
from app.models.base import get_utc_now


class SOSService:
    @staticmethod
    def create_sos(db: Session, sos_data: SOSCreate, citizen: Optional[User] = None) -> SOSAlert:
        # Generate message_id if not supplied by offline device
        message_id = sos_data.message_id or f"VJ-SOS-{uuid.uuid4().hex[:8].upper()}"
        
        # Check if message_id already exists to prevent duplicate entries
        existing = db.query(SOSAlert).filter(SOSAlert.message_id == message_id).first()
        if existing:
            return existing

        now = get_utc_now()
        sos = SOSAlert(
            message_id=message_id,
            citizen_id=citizen.id if citizen else None,
            origin_device_id=sos_data.origin_device_id,
            message=sos_data.message,
            latitude=sos_data.latitude,
            longitude=sos_data.longitude,
            severity=sos_data.severity,
            status=SOSStatus.ACTIVE,
            created_at=now,
            received_at=now,
        )
        db.add(sos)
        db.commit()
        db.refresh(sos)
        return sos

    @staticmethod
    def get_citizen_sos_list(db: Session, citizen_id: str) -> List[SOSAlert]:
        return db.query(SOSAlert).filter(
            SOSAlert.citizen_id == citizen_id
        ).order_by(SOSAlert.created_at.desc()).all()

    @staticmethod
    def get_sos_by_id(db: Session, sos_id: str) -> Optional[SOSAlert]:
        return db.query(SOSAlert).filter(SOSAlert.id == sos_id).first()

    @staticmethod
    def get_all_sos(
        db: Session,
        status_filter: Optional[SOSStatus] = None,
        severity_filter: Optional[SOSSeverity] = None,
        skip: int = 0,
        limit: Optional[int] = 1000
    ) -> List[SOSAlert]:
        query = db.query(SOSAlert)
        if status_filter:
            query = query.filter(SOSAlert.status == status_filter)
        if severity_filter:
            query = query.filter(SOSAlert.severity == severity_filter)
        query = query.order_by(SOSAlert.created_at.desc()).offset(skip)
        if limit:
            query = query.limit(limit)
        return query.all()

    @staticmethod
    def update_sos(db: Session, sos_id: str, update_data: SOSUpdate) -> Optional[SOSAlert]:
        sos = db.query(SOSAlert).filter(SOSAlert.id == sos_id).first()
        if not sos:
            return None

        if update_data.status is not None:
            sos.status = update_data.status
            if update_data.status == SOSStatus.RESOLVED:
                sos.resolved_at = get_utc_now()
        if update_data.severity is not None:
            sos.severity = update_data.severity

        db.commit()
        db.refresh(sos)
        return sos
