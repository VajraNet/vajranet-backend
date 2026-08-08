from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.models.sos import SOSAlert, SOSStatus, SOSSeverity
from app.models.incident import Incident, IncidentStatus, IncidentSeverity
from app.models.shelter import Shelter, ShelterStatus
from app.models.hospital import Hospital
from app.models.announcement import Announcement
from app.models.volunteer import Volunteer, VolunteerTask, TaskStatus
from app.models.fundraiser import FundraisingCampaign, FundraiserStatus
from app.schemas.dashboard import CitizenOverviewResponse, GovernmentOverviewResponse, VolunteerOverviewResponse
from app.schemas.sos import SOSResponse
from app.schemas.incident import IncidentResponse
from app.schemas.announcement import AnnouncementResponse
from app.schemas.volunteer import VolunteerTaskResponse
from app.services.resource_service import ResourceService
from app.services.announcement_service import AnnouncementService
from app.services.volunteer_service import VolunteerService


class DashboardService:
    @staticmethod
    def get_citizen_overview(db: Session, user: User, lat: Optional[float] = None, lon: Optional[float] = None) -> CitizenOverviewResponse:
        # Active SOS
        active_sos_model = db.query(SOSAlert).filter(
            SOSAlert.citizen_id == user.id,
            SOSAlert.status.in_([SOSStatus.ACTIVE, SOSStatus.ACKNOWLEDGED, SOSStatus.IN_PROGRESS])
        ).order_by(SOSAlert.created_at.desc()).first()

        active_sos_resp = SOSResponse.model_validate(active_sos_model) if active_sos_model else None

        # User's incidents
        my_incidents_query = db.query(Incident).filter(Incident.reported_by == user.id)
        total_my_incidents = my_incidents_query.count()
        recent_my_incidents = my_incidents_query.order_by(Incident.created_at.desc()).limit(5).all()

        my_incidents_resp = [
            IncidentResponse(
                id=inc.id,
                message_id=inc.message_id,
                reported_by=inc.reported_by,
                title=inc.title,
                description=inc.description,
                type=inc.type,
                latitude=inc.latitude,
                longitude=inc.longitude,
                severity=inc.severity,
                status=inc.status,
                media_urls=inc.media_urls,
                created_at=inc.created_at,
                updated_at=inc.updated_at
            ) for inc in recent_my_incidents
        ]

        # Nearby resources
        nearby_shelters_count = 0
        nearby_hospitals_count = 0
        if lat is not None and lon is not None:
            nearby_shelters_count = len(ResourceService.get_nearby_shelters(db, lat, lon, radius_km=25.0))
            nearby_hospitals_count = len(ResourceService.get_nearby_hospitals(db, lat, lon, radius_km=25.0))
        else:
            nearby_shelters_count = db.query(Shelter).filter(Shelter.status != ShelterStatus.CLOSED).count()
            nearby_hospitals_count = db.query(Hospital).count()

        # Announcements
        active_announcements = AnnouncementService.get_active_announcements(db)[:5]
        active_ann_resp = [AnnouncementResponse.model_validate(a) for a in active_announcements]

        return CitizenOverviewResponse(
            active_sos=active_sos_resp,
            total_my_incidents=total_my_incidents,
            my_incidents=my_incidents_resp,
            nearby_shelters_count=nearby_shelters_count,
            nearby_hospitals_count=nearby_hospitals_count,
            active_announcements=active_ann_resp
        )

    @staticmethod
    def get_government_overview(db: Session) -> GovernmentOverviewResponse:
        active_sos_count = db.query(SOSAlert).filter(
            SOSAlert.status.in_([SOSStatus.ACTIVE, SOSStatus.ACKNOWLEDGED, SOSStatus.IN_PROGRESS])
        ).count()

        active_incidents_count = db.query(Incident).filter(
            Incident.status.in_([IncidentStatus.REPORTED, IncidentStatus.VERIFIED, IncidentStatus.IN_PROGRESS])
        ).count()

        critical_incidents_count = db.query(Incident).filter(
            Incident.severity == IncidentSeverity.CRITICAL,
            Incident.status != IncidentStatus.RESOLVED
        ).count()

        volunteers_responding_count = db.query(
            func.count(func.distinct(VolunteerTask.volunteer_id))
        ).filter(VolunteerTask.status.in_([TaskStatus.ACCEPTED, TaskStatus.IN_PROGRESS])).scalar() or 0

        available_shelters_count = db.query(Shelter).filter(Shelter.status == ShelterStatus.OPEN).count()

        total_shelter_capacity = db.query(func.sum(Shelter.capacity)).scalar() or 0
        total_shelter_occupied = db.query(func.sum(Shelter.occupied)).scalar() or 0

        available_hospital_beds = db.query(func.sum(Hospital.available_beds)).scalar() or 0
        available_icu_beds = db.query(func.sum(Hospital.icu_available)).scalar() or 0

        active_announcements_count = len(AnnouncementService.get_active_announcements(db))

        recent_incidents = db.query(Incident).order_by(Incident.created_at.desc()).limit(5).all()
        recent_sos = db.query(SOSAlert).order_by(SOSAlert.created_at.desc()).limit(5).all()

        return GovernmentOverviewResponse(
            active_sos_count=active_sos_count,
            active_incidents_count=active_incidents_count,
            critical_incidents_count=critical_incidents_count,
            volunteers_responding_count=volunteers_responding_count,
            available_shelters_count=available_shelters_count,
            total_shelter_capacity=int(total_shelter_capacity),
            total_shelter_occupied=int(total_shelter_occupied),
            available_hospital_beds=int(available_hospital_beds),
            available_icu_beds=int(available_icu_beds),
            active_announcements_count=active_announcements_count,
            recent_incidents=[
                IncidentResponse(
                    id=inc.id,
                    message_id=inc.message_id,
                    reported_by=inc.reported_by,
                    title=inc.title,
                    description=inc.description,
                    type=inc.type,
                    latitude=inc.latitude,
                    longitude=inc.longitude,
                    severity=inc.severity,
                    status=inc.status,
                    media_urls=inc.media_urls,
                    created_at=inc.created_at,
                    updated_at=inc.updated_at
                ) for inc in recent_incidents
            ],
            recent_sos=[SOSResponse.model_validate(s) for s in recent_sos]
        )

    @staticmethod
    def get_volunteer_overview(db: Session, user: User, lat: Optional[float] = None, lon: Optional[float] = None) -> VolunteerOverviewResponse:
        vol = VolunteerService.get_or_create_profile(db, user)

        available_tasks_count = db.query(Incident).filter(
            Incident.status.in_([IncidentStatus.REPORTED, IncidentStatus.VERIFIED])
        ).count()

        tasks_query = db.query(VolunteerTask).filter(VolunteerTask.volunteer_id == vol.id)
        accepted_tasks_count = tasks_query.filter(VolunteerTask.status == TaskStatus.ACCEPTED).count()
        active_tasks_count = tasks_query.filter(VolunteerTask.status == TaskStatus.IN_PROGRESS).count()
        completed_tasks_count = tasks_query.filter(VolunteerTask.status == TaskStatus.COMPLETED).count()

        my_active_tasks = tasks_query.filter(
            VolunteerTask.status.in_([TaskStatus.ACCEPTED, TaskStatus.IN_PROGRESS])
        ).all()

        nearby_incidents_count = db.query(Incident).filter(Incident.status != IncidentStatus.RESOLVED).count()
        active_fundraisers_count = db.query(FundraisingCampaign).filter(FundraisingCampaign.status == FundraiserStatus.ACTIVE).count()

        return VolunteerOverviewResponse(
            available_tasks_count=available_tasks_count,
            accepted_tasks_count=accepted_tasks_count,
            active_tasks_count=active_tasks_count,
            completed_tasks_count=completed_tasks_count,
            my_active_tasks=[VolunteerTaskResponse.model_validate(t) for t in my_active_tasks],
            nearby_incidents_count=nearby_incidents_count,
            active_fundraisers_count=active_fundraisers_count,
            volunteer_status=vol.availability_status.value
        )
