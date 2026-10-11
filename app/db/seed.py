import logging
from sqlalchemy.orm import Session
from app.models.shelter import Shelter, ShelterStatus
from app.models.hospital import Hospital, HospitalType
from app.models.relief_center import ReliefCenter, ReliefCenterStatus
from app.models.announcement import Announcement, AnnouncementType, AnnouncementPriority
from app.models.sos import SOSAlert, SOSSeverity, SOSStatus

logger = logging.getLogger(__name__)


def seed_default_data_if_empty(db: Session) -> None:
    """
    Idempotent database seeder.
    Populates default shelters, hospitals, relief centers, and emergency broadcasts
    if the database is newly created (e.g. fresh Railway PostgreSQL deploy).
    """
    try:
        if db.query(Shelter).first():
            return

        logger.info("Fresh database detected. Seeding initial VajraNet operational data...")

        # 1. Default Shelters
        shelters = [
            Shelter(
                name="Sector 4 Indoor Stadium Relief Camp",
                description="Large covered shelter with sanitary facilities, clean water supply, and basic first-aid.",
                address="Sports Complex, Sector 4, Main Road",
                latitude=28.6175,
                longitude=77.2080,
                capacity=800,
                occupied=460,
                status=ShelterStatus.OPEN,
                is_private=False
            ),
            Shelter(
                name="Model High School Emergency Shelter",
                description="School gymnasium converted to emergency shelter with bedding and warm meals.",
                address="Station Road, Gate 1, Near Railway Station",
                latitude=28.6210,
                longitude=77.2210,
                capacity=400,
                occupied=380,
                status=ShelterStatus.OPEN,
                is_private=False
            ),
            Shelter(
                name="Community Hall Block B Evacuation Point",
                description="Designated NDRF evacuation holding point with satellite comms backup.",
                address="Community Hall, Block B, Sector 11",
                latitude=28.6090,
                longitude=77.1970,
                capacity=600,
                occupied=210,
                status=ShelterStatus.OPEN,
                is_private=False
            )
        ]
        db.add_all(shelters)

        # 2. Default Hospitals
        hospitals = [
            Hospital(
                name="Apex Trauma & Emergency Hospital",
                address="Ring Road, Sector 7",
                latitude=28.6155,
                longitude=77.2140,
                type=HospitalType.GOVERNMENT,
                total_beds=200,
                available_beds=42,
                icu_total=30,
                icu_available=8,
                emergency_available=True,
                contact_phone="+91-11-2301-4455"
            ),
            Hospital(
                name="Red Cross Field Hospital",
                address="Naval Dock Gate 3, Port Area",
                latitude=28.6245,
                longitude=77.1950,
                type=HospitalType.PRIVATE,
                total_beds=80,
                available_beds=28,
                icu_total=10,
                icu_available=4,
                emergency_available=True,
                contact_phone="+91-11-2301-8899"
            )
        ]
        db.add_all(hospitals)

        # 3. Default Relief Centers
        relief_centers = [
            ReliefCenter(
                name="VajraNet Central Ration & Water Depot",
                description="Primary emergency supply depot for food packets, potable water, and medical kits.",
                address="Community Hall Block B",
                latitude=28.6100,
                longitude=77.2000,
                items_available=["Food", "Water", "Medicine", "Blankets"],
                status=ReliefCenterStatus.OPERATIONAL
            ),
            ReliefCenter(
                name="Station Road Water Distribution Point",
                description="Clean water filtration station and hydration point for evacuees.",
                address="Station Road, Near Bus Stand",
                latitude=28.6220,
                longitude=77.2190,
                items_available=["Water", "Electrolytes"],
                status=ReliefCenterStatus.OPERATIONAL
            )
        ]
        db.add_all(relief_centers)

        # 4. Default Emergency Announcement
        announcement = Announcement(
            title="NDRF High Tide & Severe Weather Advisory",
            content="Heavy rainfall and flash flood warnings active in coastal zones. Evacuation holding camps in Sector 4 and Block B are fully operational. Please conserve emergency battery and stay tuned to VajraNet alerts.",
            type=AnnouncementType.EVACUATION,
            priority=AnnouncementPriority.CRITICAL,
            target_area="Zone 4 Coastal & Low-Lying Sectors",
            author_id=None
        )
        db.add(announcement)

        db.commit()
        logger.info("Initial operational data seeded successfully.")
    except Exception as exc:
        db.rollback()
        logger.warning(f"Initial data seed notice: {exc}")
