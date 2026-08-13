import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.core.response import success_response
from app.models.user import User
from app.models.trusted_device import TrustedDevice
from app.models.sos import SOSAlert
from app.schemas.trusted_device import TrustedDeviceCreate, TrustedDeviceResponse, SOSRelayRequest

router = APIRouter(prefix="/devices/trusted", tags=["trusted-devices"])

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def register_trusted_device(
    payload: TrustedDeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register a phone number as a trusted emergency SMS relay device (GOVERNMENT or VOLUNTEER only)."""
    if current_user.role not in ["GOVERNMENT", "VOLUNTEER", "SUPERADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only government officials and volunteers can register trusted relay devices."
        )

    # Check duplicate phone
    existing = db.query(TrustedDevice).filter(TrustedDevice.phone == payload.phone).first()
    if existing:
        existing.is_active = True
        existing.name = payload.name
        existing.latitude = payload.latitude
        existing.longitude = payload.longitude
        db.commit()
        db.refresh(existing)
        return success_response(data=TrustedDeviceResponse.from_orm(existing).dict(), message="Trusted device updated")

    new_device = TrustedDevice(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=payload.name,
        phone=payload.phone,
        role=payload.role or current_user.role,
        latitude=payload.latitude,
        longitude=payload.longitude,
        is_active=True
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)

    return success_response(data=TrustedDeviceResponse.from_orm(new_device).dict(), message="Trusted relay device registered")

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

    res_list = [TrustedDeviceResponse.from_orm(d).dict() for d in devices]
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

    if device.user_id != current_user.id and current_user.role != "GOVERNMENT":
        raise HTTPException(status_code=403, detail="Not authorized to delete this device")

    device.is_active = False
    db.commit()
    return success_response(message="Trusted device deactivated")

@router.post("/relay-sos", response_model=dict, status_code=status.HTTP_201_CREATED)
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
            "status": sos.status,
            "latitude": sos.latitude,
            "longitude": sos.longitude,
            "source": "SMS_RELAY"
        },
        message="SMS Emergency SOS successfully ingested into Government Command Center!"
    )
