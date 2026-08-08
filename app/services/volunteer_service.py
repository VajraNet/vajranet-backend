from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.volunteer import Volunteer, VolunteerTask, VolunteerAvailability, TaskStatus
from app.models.incident import Incident, IncidentStatus
from app.models.fundraiser import FundraisingCampaign, FundraiserStatus
from app.models.user import User
from app.schemas.volunteer import VolunteerProfileCreate, VolunteerProfileUpdate, TaskStatusUpdate
from app.schemas.fundraiser import FundraiserCreate, FundraiserUpdate
from app.models.base import get_utc_now


class VolunteerService:
    @staticmethod
    def get_or_create_profile(db: Session, user: User, profile_data: Optional[VolunteerProfileCreate] = None) -> Volunteer:
        vol = db.query(Volunteer).filter(Volunteer.user_id == user.id).first()
        if not vol:
            vol = Volunteer(
                user_id=user.id,
                availability_status=profile_data.availability_status if profile_data else VolunteerAvailability.AVAILABLE,
                phone=profile_data.phone if profile_data else user.phone,
                location=profile_data.location if profile_data else None,
                created_at=get_utc_now(),
                updated_at=get_utc_now(),
            )
            vol.skills = profile_data.skills if profile_data else ["General Relief"]
            db.add(vol)
            db.commit()
            db.refresh(vol)
        return vol

    @staticmethod
    def update_profile(db: Session, user: User, data: VolunteerProfileUpdate) -> Volunteer:
        vol = VolunteerService.get_or_create_profile(db, user)
        if data.skills is not None:
            vol.skills = data.skills
        if data.availability_status is not None:
            vol.availability_status = data.availability_status
        if data.phone is not None:
            vol.phone = data.phone
        if data.location is not None:
            vol.location = data.location

        vol.updated_at = get_utc_now()
        db.commit()
        db.refresh(vol)
        return vol

    @staticmethod
    def get_claimable_incidents(db: Session, skip: int = 0, limit: int = 100) -> List[Incident]:
        return db.query(Incident).filter(
            Incident.status.in_([IncidentStatus.REPORTED, IncidentStatus.VERIFIED, IncidentStatus.IN_PROGRESS])
        ).order_by(Incident.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def accept_incident_task(db: Session, user: User, incident_id: str, notes: Optional[str] = None) -> Optional[VolunteerTask]:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            return None

        volunteer = VolunteerService.get_or_create_profile(db, user)

        # Check if already assigned to this volunteer
        existing_task = db.query(VolunteerTask).filter(
            VolunteerTask.incident_id == incident_id,
            VolunteerTask.volunteer_id == volunteer.id,
            VolunteerTask.status.in_([TaskStatus.ASSIGNED, TaskStatus.ACCEPTED, TaskStatus.IN_PROGRESS])
        ).first()
        if existing_task:
            return existing_task

        task = VolunteerTask(
            incident_id=incident_id,
            volunteer_id=volunteer.id,
            status=TaskStatus.ACCEPTED,
            notes=notes,
            assigned_at=get_utc_now(),
            updated_at=get_utc_now(),
        )
        db.add(task)

        # Move incident to IN_PROGRESS
        incident.status = IncidentStatus.IN_PROGRESS
        incident.updated_at = get_utc_now()

        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def update_task_status(db: Session, user: User, incident_id: str, update_data: TaskStatusUpdate) -> Optional[VolunteerTask]:
        volunteer = db.query(Volunteer).filter(Volunteer.user_id == user.id).first()
        if not volunteer:
            return None

        task = db.query(VolunteerTask).filter(
            VolunteerTask.incident_id == incident_id,
            VolunteerTask.volunteer_id == volunteer.id
        ).first()
        if not task:
            return None

        task.status = update_data.status
        if update_data.notes:
            task.notes = update_data.notes
        task.updated_at = get_utc_now()

        if update_data.status == TaskStatus.COMPLETED:
            task.completed_at = get_utc_now()
            # If incident has no other active tasks, optionally mark resolved
            incident = db.query(Incident).filter(Incident.id == incident_id).first()
            if incident:
                incident.status = IncidentStatus.RESOLVED
                incident.updated_at = get_utc_now()

        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def get_my_tasks(db: Session, user: User) -> List[VolunteerTask]:
        volunteer = db.query(Volunteer).filter(Volunteer.user_id == user.id).first()
        if not volunteer:
            return []
        return db.query(VolunteerTask).filter(
            VolunteerTask.volunteer_id == volunteer.id
        ).order_by(VolunteerTask.assigned_at.desc()).all()

    # -------------------------------------------------------------
    # FUNDRAISERS
    # -------------------------------------------------------------
    @staticmethod
    def create_fundraiser(db: Session, user: User, data: FundraiserCreate) -> FundraisingCampaign:
        camp = FundraisingCampaign(
            title=data.title,
            description=data.description,
            target_amount=data.target_amount,
            raised_amount=0.0,
            beneficiary=data.beneficiary,
            status=FundraiserStatus.ACTIVE,
            created_by=user.id,
            created_at=get_utc_now(),
            updated_at=get_utc_now(),
        )
        db.add(camp)
        db.commit()
        db.refresh(camp)
        return camp

    @staticmethod
    def get_fundraisers(db: Session, status: Optional[FundraiserStatus] = None, skip: int = 0, limit: int = 100) -> List[FundraisingCampaign]:
        query = db.query(FundraisingCampaign)
        if status:
            query = query.filter(FundraisingCampaign.status == status)
        return query.order_by(FundraisingCampaign.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_fundraiser(db: Session, fundraiser_id: str, data: FundraiserUpdate) -> Optional[FundraisingCampaign]:
        camp = db.query(FundraisingCampaign).filter(FundraisingCampaign.id == fundraiser_id).first()
        if not camp:
            return None

        if data.title is not None:
            camp.title = data.title
        if data.description is not None:
            camp.description = data.description
        if data.target_amount is not None:
            camp.target_amount = data.target_amount
        if data.raised_amount is not None:
            camp.raised_amount = data.raised_amount
        if data.beneficiary is not None:
            camp.beneficiary = data.beneficiary
        if data.status is not None:
            camp.status = data.status

        camp.updated_at = get_utc_now()
        db.commit()
        db.refresh(camp)
        return camp
