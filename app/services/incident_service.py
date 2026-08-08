import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.incident import Incident, IncidentType, IncidentSeverity, IncidentStatus
from app.models.user import User
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.models.base import get_utc_now


class IncidentService:
    @staticmethod
    def create_incident(db: Session, incident_data: IncidentCreate, reporter: Optional[User] = None) -> Incident:
        message_id = incident_data.message_id or f"VJ-INC-{uuid.uuid4().hex[:8].upper()}"
        
        # Check if already exists by message_id
        existing = db.query(Incident).filter(Incident.message_id == message_id).first()
        if existing:
            return existing

        incident = Incident(
            message_id=message_id,
            reported_by=reporter.id if reporter else None,
            title=incident_data.title,
            description=incident_data.description,
            type=incident_data.type,
            latitude=incident_data.latitude,
            longitude=incident_data.longitude,
            severity=incident_data.severity,
            status=IncidentStatus.REPORTED,
            created_at=get_utc_now(),
            updated_at=get_utc_now(),
        )
        incident.media_urls = incident_data.media_urls or []

        db.add(incident)
        db.commit()
        db.refresh(incident)
        return incident

    @staticmethod
    def get_citizen_incidents(db: Session, citizen_id: str) -> List[Incident]:
        return db.query(Incident).filter(
            Incident.reported_by == citizen_id
        ).order_by(Incident.created_at.desc()).all()

    @staticmethod
    def get_incident_by_id(db: Session, incident_id: str) -> Optional[Incident]:
        return db.query(Incident).filter(Incident.id == incident_id).first()

    @staticmethod
    def get_all_incidents(
        db: Session,
        type_filter: Optional[IncidentType] = None,
        severity_filter: Optional[IncidentSeverity] = None,
        status_filter: Optional[IncidentStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Incident]:
        query = db.query(Incident)
        if type_filter:
            query = query.filter(Incident.type == type_filter)
        if severity_filter:
            query = query.filter(Incident.severity == severity_filter)
        if status_filter:
            query = query.filter(Incident.status == status_filter)
        return query.order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_incident(db: Session, incident_id: str, update_data: IncidentUpdate) -> Optional[Incident]:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return None

        if update_data.title is not None:
            incident.title = update_data.title
        if update_data.description is not None:
            incident.description = update_data.description
        if update_data.type is not None:
            incident.type = update_data.type
        if update_data.severity is not None:
            incident.severity = update_data.severity
        if update_data.status is not None:
            incident.status = update_data.status
        if update_data.media_urls is not None:
            incident.media_urls = update_data.media_urls

        incident.updated_at = get_utc_now()
        db.commit()
        db.refresh(incident)
        return incident
