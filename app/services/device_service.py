from typing import Optional
from sqlalchemy.orm import Session
from app.models.device import Device
from app.models.user import User
from app.schemas.device import DeviceRegisterRequest
from app.models.base import get_utc_now
from typing import List
from app.core.haversine import calculate_haversine_distance

class DeviceService:
    @staticmethod
    def register_or_update_device(db: Session, data: DeviceRegisterRequest, user: Optional[User] = None) -> Device:
        device = db.query(Device).filter(Device.device_id == data.device_id).first()
        now = get_utc_now()
        if not device:
            device = Device(
                device_id=data.device_id,
                device_type=data.device_type,
                owner_id=user.id if user else None,
                last_seen_at=now,
                battery_level=data.battery_level,
                mesh_hop_count=data.mesh_hop_count,
                latitude=data.latitude,
                longitude=data.longitude,
                created_at=now,
            )
            db.add(device)
        else:
            device.device_type = data.device_type
            if user:
                device.owner_id = user.id
            device.last_seen_at = now
            if data.battery_level is not None:
                device.battery_level = data.battery_level
            device.mesh_hop_count = data.mesh_hop_count
            if data.latitude is not None:
                device.latitude = data.latitude
            if data.longitude is not None:
                device.longitude = data.longitude

        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def get_device_by_id(db: Session, device_id: str) -> Optional[Device]:
        return db.query(Device).filter(Device.device_id == device_id).first()

    @staticmethod
    def get_all_devices(db: Session, device_type: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Device]:
        query = db.query(Device)
        if device_type:
            query = query.filter(Device.device_type == device_type)
        return query.order_by(Device.last_seen_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_nearby_devices(db: Session, latitude: float, longitude: float, radius_km: float = 15.0) -> List[Device]:
        all_devices = db.query(Device).filter(Device.latitude.isnot(None), Device.longitude.isnot(None)).all()
        results = []
        for d in all_devices:
            dist = calculate_haversine_distance(latitude, longitude, d.latitude, d.longitude)
            if dist <= radius_km:
                # Instead of creating a new field, we'll return the device. 
                # The schema doesn't have distance_km, so we just sort them.
                results.append((d, dist))
        
        results.sort(key=lambda item: item[1])
        return [item[0] for item in results]
