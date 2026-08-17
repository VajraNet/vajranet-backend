from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from app.models.shelter import Shelter, ShelterStatus
from app.models.hospital import Hospital, HospitalType
from app.models.relief_center import ReliefCenter, ReliefCenterStatus
from app.models.user import User
from app.schemas.shelter import ShelterCreate, ShelterUpdate, ShelterResponse
from app.schemas.hospital import HospitalCreate, HospitalUpdate, HospitalResponse
from app.schemas.relief_center import ReliefCenterCreate, ReliefCenterUpdate, ReliefCenterResponse
from app.core.haversine import calculate_haversine_distance
from app.models.base import get_utc_now


class ResourceService:
    # -------------------------------------------------------------
    # SHELTERS
    # -------------------------------------------------------------
    @staticmethod
    def create_shelter(db: Session, shelter_data: ShelterCreate, creator: Optional[User] = None) -> Shelter:
        shelter = Shelter(
            name=shelter_data.name,
            description=shelter_data.description,
            latitude=shelter_data.latitude,
            longitude=shelter_data.longitude,
            address=shelter_data.address,
            capacity=shelter_data.capacity,
            occupied=shelter_data.occupied,
            status=shelter_data.status,
            is_private=shelter_data.is_private,
            managed_by=creator.id if creator else None,
            created_at=get_utc_now(),
            updated_at=get_utc_now(),
        )
        db.add(shelter)
        db.commit()
        db.refresh(shelter)
        return shelter

    @staticmethod
    def update_shelter(db: Session, shelter_id: str, update_data: ShelterUpdate) -> Optional[Shelter]:
        shelter = db.query(Shelter).filter(Shelter.id == shelter_id).first()
        if not shelter:
            return None

        if update_data.name is not None:
            shelter.name = update_data.name
        if update_data.description is not None:
            shelter.description = update_data.description
        if update_data.latitude is not None:
            shelter.latitude = update_data.latitude
        if update_data.longitude is not None:
            shelter.longitude = update_data.longitude
        if update_data.address is not None:
            shelter.address = update_data.address
        if update_data.capacity is not None:
            shelter.capacity = update_data.capacity
        if update_data.occupied is not None:
            shelter.occupied = update_data.occupied
        if update_data.status is not None:
            shelter.status = update_data.status

        shelter.updated_at = get_utc_now()
        db.commit()
        db.refresh(shelter)
        return shelter

    @staticmethod
    def get_shelter_by_id(db: Session, shelter_id: str) -> Optional[Shelter]:
        return db.query(Shelter).filter(Shelter.id == shelter_id).first()

    @staticmethod
    def get_all_shelters(
        db: Session,
        status_filter: Optional[ShelterStatus] = None,
        is_private: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Shelter]:
        query = db.query(Shelter)
        if status_filter:
            query = query.filter(Shelter.status == status_filter)
        if is_private is not None:
            query = query.filter(Shelter.is_private == is_private)
        return query.order_by(Shelter.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_nearby_shelters(db: Session, latitude: float, longitude: float, radius_km: float = 15.0) -> List[ShelterResponse]:
        all_shelters = db.query(Shelter).all()
        results = []
        for s in all_shelters:
            dist = calculate_haversine_distance(latitude, longitude, s.latitude, s.longitude)
            if dist <= radius_km:
                available_cap = max(0, s.capacity - s.occupied)
                s_resp = ShelterResponse(
                    id=s.id,
                    name=s.name,
                    description=s.description,
                    latitude=s.latitude,
                    longitude=s.longitude,
                    address=s.address,
                    capacity=s.capacity,
                    occupied=s.occupied,
                    available_capacity=available_cap,
                    status=s.status,
                    is_private=s.is_private,
                    managed_by=s.managed_by,
                    distance_km=dist,
                    created_at=s.created_at,
                    updated_at=s.updated_at
                )
                results.append(s_resp)

        # Sort ascending by distance
        results.sort(key=lambda item: item.distance_km or 0.0)
        return results

    # -------------------------------------------------------------
    # HOSPITALS
    # -------------------------------------------------------------
    @staticmethod
    def create_hospital(db: Session, hospital_data: HospitalCreate, creator: Optional[User] = None) -> Hospital:
        hospital = Hospital(
            name=hospital_data.name,
            type=hospital_data.type,
            latitude=hospital_data.latitude,
            longitude=hospital_data.longitude,
            address=hospital_data.address,
            emergency_available=hospital_data.emergency_available,
            total_beds=hospital_data.total_beds,
            available_beds=hospital_data.available_beds,
            icu_total=hospital_data.icu_total,
            icu_available=hospital_data.icu_available,
            managed_by=creator.id if creator else None,
            created_at=get_utc_now(),
            updated_at=get_utc_now(),
        )
        db.add(hospital)
        db.commit()
        db.refresh(hospital)
        return hospital

    @staticmethod
    def update_hospital(db: Session, hospital_id: str, update_data: HospitalUpdate) -> Optional[Hospital]:
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
        if not hospital:
            return None

        if update_data.name is not None:
            hospital.name = update_data.name
        if update_data.type is not None:
            hospital.type = update_data.type
        if update_data.latitude is not None:
            hospital.latitude = update_data.latitude
        if update_data.longitude is not None:
            hospital.longitude = update_data.longitude
        if update_data.address is not None:
            hospital.address = update_data.address
        if update_data.emergency_available is not None:
            hospital.emergency_available = update_data.emergency_available
        if update_data.total_beds is not None:
            hospital.total_beds = update_data.total_beds
        if update_data.available_beds is not None:
            hospital.available_beds = update_data.available_beds
        if update_data.icu_total is not None:
            hospital.icu_total = update_data.icu_total
        if update_data.icu_available is not None:
            hospital.icu_available = update_data.icu_available

        hospital.updated_at = get_utc_now()
        db.commit()
        db.refresh(hospital)
        return hospital

    @staticmethod
    def get_hospital_by_id(db: Session, hospital_id: str) -> Optional[Hospital]:
        return db.query(Hospital).filter(Hospital.id == hospital_id).first()

    @staticmethod
    def get_all_hospitals(
        db: Session,
        type_filter: Optional[HospitalType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Hospital]:
        query = db.query(Hospital)
        if type_filter:
            query = query.filter(Hospital.type == type_filter)
        return query.order_by(Hospital.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_nearby_hospitals(db: Session, latitude: float, longitude: float, radius_km: float = 15.0) -> List[HospitalResponse]:
        all_hospitals = db.query(Hospital).all()
        results = []
        for h in all_hospitals:
            dist = calculate_haversine_distance(latitude, longitude, h.latitude, h.longitude)
            if dist <= radius_km:
                h_resp = HospitalResponse(
                    id=h.id,
                    name=h.name,
                    type=h.type,
                    latitude=h.latitude,
                    longitude=h.longitude,
                    address=h.address,
                    emergency_available=h.emergency_available,
                    total_beds=h.total_beds,
                    available_beds=h.available_beds,
                    icu_total=h.icu_total,
                    icu_available=h.icu_available,
                    managed_by=h.managed_by,
                    distance_km=dist,
                    created_at=h.created_at,
                    updated_at=h.updated_at
                )
                results.append(h_resp)

        results.sort(key=lambda item: item.distance_km or 0.0)
        return results

    # -------------------------------------------------------------
    # RELIEF CENTERS
    # -------------------------------------------------------------
    @staticmethod
    def create_relief_center(db: Session, rc_data: ReliefCenterCreate, creator: Optional[User] = None) -> ReliefCenter:
        rc = ReliefCenter(
            name=rc_data.name,
            description=rc_data.description,
            latitude=rc_data.latitude,
            longitude=rc_data.longitude,
            address=rc_data.address,
            status=rc_data.status,
            managed_by=creator.id if creator else None,
            created_at=get_utc_now(),
            updated_at=get_utc_now(),
        )
        rc.items_available = rc_data.items_available
        db.add(rc)
        db.commit()
        db.refresh(rc)
        return rc

    @staticmethod
    def update_relief_center(db: Session, rc_id: str, update_data: ReliefCenterUpdate) -> Optional[ReliefCenter]:
        rc = db.query(ReliefCenter).filter(ReliefCenter.id == rc_id).first()
        if not rc:
            return None

        if update_data.name is not None:
            rc.name = update_data.name
        if update_data.description is not None:
            rc.description = update_data.description
        if update_data.latitude is not None:
            rc.latitude = update_data.latitude
        if update_data.longitude is not None:
            rc.longitude = update_data.longitude
        if update_data.address is not None:
            rc.address = update_data.address
        if update_data.items_available is not None:
            rc.items_available = update_data.items_available
        if update_data.status is not None:
            rc.status = update_data.status

        rc.updated_at = get_utc_now()
        db.commit()
        db.refresh(rc)
        return rc

    @staticmethod
    def get_relief_center_by_id(db: Session, rc_id: str) -> Optional[ReliefCenter]:
        return db.query(ReliefCenter).filter(ReliefCenter.id == rc_id).first()

    @staticmethod
    def get_all_relief_centers(
        db: Session,
        status_filter: Optional[ReliefCenterStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReliefCenter]:
        query = db.query(ReliefCenter)
        if status_filter:
            query = query.filter(ReliefCenter.status == status_filter)
        return query.order_by(ReliefCenter.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_nearby_relief_centers(db: Session, latitude: float, longitude: float, radius_km: float = 15.0) -> List[ReliefCenterResponse]:
        all_rcs = db.query(ReliefCenter).all()
        results = []
        for rc in all_rcs:
            dist = calculate_haversine_distance(latitude, longitude, rc.latitude, rc.longitude)
            if dist <= radius_km:
                rc_resp = ReliefCenterResponse(
                    id=rc.id,
                    name=rc.name,
                    description=rc.description,
                    latitude=rc.latitude,
                    longitude=rc.longitude,
                    address=rc.address,
                    items_available=rc.items_available,
                    status=rc.status,
                    managed_by=rc.managed_by,
                    distance_km=dist,
                    created_at=rc.created_at,
                    updated_at=rc.updated_at
                )
                results.append(rc_resp)

        results.sort(key=lambda item: item.distance_km or 0.0)
        return results

    @staticmethod
    def delete_shelter(db: Session, shelter_id: str) -> bool:
        shelter = db.query(Shelter).filter(Shelter.id == shelter_id).first()
        if not shelter:
            return False
        db.delete(shelter)
        db.commit()
        return True

    @staticmethod
    def delete_hospital(db: Session, hospital_id: str) -> bool:
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
        if not hospital:
            return False
        db.delete(hospital)
        db.commit()
        return True

    @staticmethod
    def delete_relief_center(db: Session, rc_id: str) -> bool:
        rc = db.query(ReliefCenter).filter(ReliefCenter.id == rc_id).first()
        if not rc:
            return False
        db.delete(rc)
        db.commit()
        return True
