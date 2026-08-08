from typing import Optional
from sqlalchemy.orm import Session
from app.models.device import Device
from app.models.user import User
from app.schemas.device import DeviceRegisterRequest
from app.models.base import get_utc_now


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

        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def get_device_by_id(db: Session, device_id: str) -> Optional[Device]:
        return db.query(Device).filter(Device.device_id == device_id).first()
