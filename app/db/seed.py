"""
VajraNet Database Seeder
Seeds initial demo shelters, hospitals, relief centers, and sample announcements.
Idempotent — skips entities that already exist.
Run standalone: python -m app.db.seed
"""
import logging
from datetime import timedelta
from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.models.base import Base, generate_uuid, get_utc_now
from app.models.shelter import Shelter, ShelterStatus
from app.models.hospital import Hospital, HospitalType
from app.models.relief_center import ReliefCenter, ReliefCenterStatus
from app.models.announcement import Announcement, AnnouncementPriority, AnnouncementType
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


def _get_or_create_system_user(db: Session) -> User:
    """Get or create a system/admin user for seeded announcements."""
    system_user = db.query(User).filter(User.phone == "0000000000").first()
    if not system_user:
        system_user = User(
            id=generate_uuid(),
            phone="0000000000",
            name="VajraNet System",
            role=UserRole.GOVERNMENT,
            is_active=True,
            created_at=get_utc_now(),
        )
        db.add(system_user)
        db.commit()
        db.refresh(system_user)
    return system_user


def seed_database(db: Session, force: bool = False) -> dict:
    """
    Seeds initial data. Skips if data already exists (idempotent).
    Set force=True to re-seed even if data exists.
    """
    stats = {"shelters": 0, "hospitals": 0, "relief_centers": 0, "announcements": 0}

    # --- SHELTERS ---
    if force or db.query(Shelter).count() == 0:
        shelters = [
            Shelter(
                name="Sector 4 Indoor Stadium Relief Camp",
                description="Large covered shelter with toilets, water supply, and basic first-aid.",
                address="Sports Complex, Sector 4, Main Road",
                latitude=28.6175,
                longitude=77.2080,
                capacity=800,
                occupied=460,
                status=ShelterStatus.OPEN,
                is_private=False,
                created_at=get_utc_now(),
                updated_at=get_utc_now(),
            ),
            Shelter(
                name="Model High School Emergency Shelter",
                description="School gymnasium converted to emergency shelter with bedding and meals.",
                address="Station Road, Gate 1, Near Railway Station",
                latitude=28.6210,
                longitude=77.2210,
                capacity=400,
                occupied=380,
                status=ShelterStatus.OPEN,
                is_private=False,
                created_at=get_utc_now(),
                updated_at=get_utc_now(),
            ),
            Shelter(
                name="Community Hall Block B Evacuation Point",
                description="Registered NDRF evacuation holding point with satellite comms.",
                address="Community Hall, Block B, Sector 11",
                latitude=28.6090,
                longitude=77.1970,
                capacity=600,
                occupied=210,
                status=ShelterStatus.OPEN,
                is_private=False,
                created_at=get_utc_now(),
                updated_at=get_utc_now(),
            ),
        ]
        db.add_all(shelters)
        db.commit()
        stats["shelters"] = len(shelters)
        logger.info(f"Seeded {len(shelters)} shelters")

    # --- HOSPITALS ---
    if force or db.query(Hospital).count() == 0:
        hospitals = [
            Hospital(
                name="Apex Trauma & Emergency Hospital",
                type=HospitalType.GOVERNMENT,
                address="Ring Road, Sector 7",
                latitude=28.6155,
                longitude=77.2140,
                total_beds=200,
                available_beds=42,
                icu_total=20,
                icu_available=8,
                emergency_available=True,
                created_at=get_utc_now(),
                updated_at=get_utc_now(),
            ),
            Hospital(
                name="Red Cross Field Hospital",
                type=HospitalType.PRIVATE,
                address="Naval Dock Gate 3, Port Area",
                latitude=28.6245,
                longitude=77.1950,
                total_beds=80,
                available_beds=28,
                icu_total=10,
                icu_available=4,
                emergency_available=True,
                created_at=get_utc_now(),
                updated_at=get_utc_now(),
            ),
        ]
        db.add_all(hospitals)
        db.commit()
        stats["hospitals"] = len(hospitals)
        logger.info(f"Seeded {len(hospitals)} hospitals")

    # --- RELIEF CENTERS ---
    if force or db.query(ReliefCenter).count() == 0:
        relief_centers = [
            ReliefCenter(
                name="VajraNet Central Ration & Water Depot",
                description="Primary government relief depot with food, clean water, medicine, and blankets.",
                address="Community Hall Block B",
                latitude=28.6100,
                longitude=77.2000,
                status=ReliefCenterStatus.OPEN,
                created_at=get_utc_now(),
                updated_at=get_utc_now(),
            ),
            ReliefCenter(
                name="Station Road Water Distribution Point",
                description="Drinking water tanker distribution, operational 6AM-8PM daily.",
                address="Station Road, Near Bus Stand",
                latitude=28.6220,
                longitude=77.2190,
                status=ReliefCenterStatus.OPEN,
                created_at=get_utc_now(),
                updated_at=get_utc_now(),
            ),
        ]
        # Set items_available via property
        relief_centers[0].items_available = ["Food", "Water", "Medicine", "Blankets"]
        relief_centers[1].items_available = ["Water"]
        db.add_all(relief_centers)
        db.commit()
        stats["relief_centers"] = len(relief_centers)
        logger.info(f"Seeded {len(relief_centers)} relief centers")

    # --- ANNOUNCEMENTS ---
    if force or db.query(Announcement).count() == 0:
        system_user = _get_or_create_system_user(db)
        expires = get_utc_now() + timedelta(days=7)
        announcements = [
            Announcement(
                title="⚠️ FLOOD ALERT: Zone B Evacuation Warning",
                content=(
                    "Residents of Zone B must evacuate immediately to designated shelters. "
                    "Move to higher ground. Do not use flooded roads. "
                    "Follow VajraNet Citizen App for shelter locations."
                ),
                type=AnnouncementType.EVACUATION,
                area="Zone B",
                priority=AnnouncementPriority.CRITICAL,
                created_by=system_user.id,
                created_at=get_utc_now(),
                expires_at=expires,
            ),
            Announcement(
                title="Clean Water Distribution Active at Station Road",
                content=(
                    "Government drinking water tankers are operational at Station Road Bus Stand. "
                    "Available 6AM–8PM daily. Carry own containers."
                ),
                type=AnnouncementType.GENERAL_UPDATE,
                area="All Districts",
                priority=AnnouncementPriority.HIGH,
                created_by=system_user.id,
                created_at=get_utc_now(),
                expires_at=expires,
            ),
            Announcement(
                title="NDRF Rescue Teams Deployed in Sectors 3, 4, 7",
                content=(
                    "National Disaster Response Force rescue teams are active in Sectors 3, 4, and 7. "
                    "Signal with torch or bright cloth from elevated position for rescue."
                ),
                type=AnnouncementType.ALERT,
                area="Sectors 3,4,7",
                priority=AnnouncementPriority.HIGH,
                created_by=system_user.id,
                created_at=get_utc_now(),
                expires_at=expires,
            ),
        ]
        db.add_all(announcements)
        db.commit()
        stats["announcements"] = len(announcements)
        logger.info(f"Seeded {len(announcements)} announcements")

    return stats


def run_seed():
    """Entry point for running seed from command line."""
    logging.basicConfig(level=logging.INFO)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        stats = seed_database(db)
        logger.info(f"Seed complete: {stats}")
        print(f"✅ Seed complete: {stats}")
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
