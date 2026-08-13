import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.core.response import success_response
from app.models.user import User
from app.models.trusted_device import TrustedDevice
from app.models.sos import SOSAlert
from app.schemas.trusted_device import TrustedDeviceCreate, SOSRelayRequest

router = APIRouter(prefix="/devices/trusted", tags=["trusted-devices"])

def device_to_dict(d: TrustedDevice) -> dict:
    return {
        "id": str(d.id),
        "user_id": str(d.user_id),
        "name": str(d.name),
        "phone": str(d.phone),
        "role": str(d.role.value if hasattr(d.role, "value") else d.role),
        "is_active": bool(d.is_active),
        "latitude": float(d.latitude) if d.latitude is not None else None,
        "longitude": float(d.longitude) if d.longitude is not None else None,
        "created_at": d.created_at.isoformat() if d.created_at else None
    }

@router.post("/", response_model=dict, status_code=status.HTTP_200_OK)
def register_trusted_device(
    payload: TrustedDeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register a phone number as a trusted emergency SMS relay device."""
    user_role = str(current_user.role.value if hasattr(current_user.role, "value") else current_user.role).upper()

    # Check duplicate phone
    existing = db.query(TrustedDevice).filter(TrustedDevice.phone == payload.phone).first()
    if existing:
        existing.is_active = True
        existing.name = payload.name
        existing.latitude = payload.latitude
        existing.longitude = payload.longitude
        db.commit()
        db.refresh(existing)
        return success_response(data=device_to_dict(existing), message="Trusted device updated")

    new_device = TrustedDevice(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=payload.name,
        phone=payload.phone,
        role=payload.role or user_role,
        latitude=payload.latitude,
        longitude=payload.longitude,
        is_active=True
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    return success_response(data=device_to_dict(new_device), message="Trusted relay device registered")

@router.get("/", response_model=dict)
def list_trusted_devices(
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    radius_km: float = Query(50.0),
    db: Session = Depends(get_db)
):
    """List active trusted relay devices for SMS fallback target selection."""
    query = db.query(TrustedDevice).filter(TrustedDevice.is_active == True)
    devices = query.all()

    if latitude is not None and longitude is not None:
        def dist(d):
            if d.latitude is None or d.longitude is None:
                return 9999.0
            return ((d.latitude - latitude)**2 + (d.longitude - longitude)**2)**0.5
        devices.sort(key=dist)

    res_list = [device_to_dict(d) for d in devices]
    return success_response(data=res_list)

@router.delete("/{device_id}", response_model=dict)
def deactivate_trusted_device(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deactivate a trusted relay device."""
    device = db.query(TrustedDevice).filter(TrustedDevice.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Trusted device not found")

    device.is_active = False
    db.commit()
    return success_response(message="Trusted device deactivated")

@router.post("/relay-sos", response_model=dict, status_code=status.HTTP_200_OK)
def relay_sms_sos(
    payload: SOSRelayRequest,
    db: Session = Depends(get_db)
):
    """Relay an emergency SMS received by a trusted device directly into the official SOS database."""
    msg_id = f"SMS-RELAY-{uuid.uuid4()}"

    sos = SOSAlert(
        id=str(uuid.uuid4()),
        message_id=msg_id,
        origin_device_id=payload.relayed_by_phone or "SMS-TRUSTED-GATEWAY",
        message=f"📱 SMS SOS ({payload.sender_phone or 'ANON'}): {payload.raw_sms_content} - {payload.notes or ''}",
        latitude=payload.latitude,
        longitude=payload.longitude,
        severity="CRITICAL",
        status="ACTIVE"
    )

    db.add(sos)
    db.commit()
    db.refresh(sos)

    return success_response(
        data={
            "id": sos.id,
            "message_id": sos.message_id,
            "status": str(sos.status.value if hasattr(sos.status, "value") else sos.status),
            "latitude": sos.latitude,
            "longitude": sos.longitude,
            "source": "SMS_RELAY"
        },
        message="SMS Emergency SOS successfully ingested into Government Command Center!"
    )
