import logging
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from app.models.offline_event import OfflineEvent, OfflineEventType, OfflineEventStatus
from app.models.sos import SOSAlert, SOSSeverity, SOSStatus
from app.models.incident import Incident, IncidentType, IncidentSeverity, IncidentStatus
from app.models.device import Device
from app.schemas.gateway import GatewaySyncRequest, GatewaySyncResponse, GatewayEventItem
from app.models.base import get_utc_now

logger = logging.getLogger(__name__)


class GatewayService:
    @staticmethod
    def process_offline_sync(db: Session, sync_data: GatewaySyncRequest) -> GatewaySyncResponse:
        """
        Idempotently processes offline events forwarded by gateways.
        Prevents duplicate creation of SOS and Incidents using unique message_id tracking.
        Preserves original created_at from victim devices while logging server received_at.
        """
        accepted: List[str] = []
        duplicates: List[str] = []
        failed: List[str] = []

        now = get_utc_now()

        # Update or register the gateway device
        gateway_device = db.query(Device).filter(Device.device_id == sync_data.gateway_id).first()
        if not gateway_device:
            gateway_device = Device(
                device_id=sync_data.gateway_id,
                device_type="GATEWAY",
                last_seen_at=now,
                created_at=now
            )
            db.add(gateway_device)
        else:
            gateway_device.last_seen_at = now

        for event in sync_data.events:
            msg_id = event.message_id.strip()

            # 1. Check for duplicate message_id
            existing_event = db.query(OfflineEvent).filter(OfflineEvent.message_id == msg_id).first()
            if existing_event:
                duplicates.append(msg_id)
                continue

            # Also check directly in SOS and Incidents tables for extra safety
            if event.type == OfflineEventType.SOS:
                if db.query(SOSAlert).filter(SOSAlert.message_id == msg_id).first():
                    duplicates.append(msg_id)
                    continue
            elif event.type == OfflineEventType.INCIDENT:
                if db.query(Incident).filter(Incident.message_id == msg_id).first():
                    duplicates.append(msg_id)
                    continue

            # 2. Process new event
            try:
                payload = event.payload or {}

                if event.type == OfflineEventType.SOS:
                    lat = float(payload.get("latitude", 0.0))
                    lon = float(payload.get("longitude", 0.0))
                    msg = str(payload.get("message", "Offline SOS Emergency Alert"))
                    sev_str = str(payload.get("severity", "CRITICAL")).upper()
                    try:
                        severity = SOSSeverity(sev_str)
                    except Exception:
                        severity = SOSSeverity.CRITICAL

                    sos_alert = SOSAlert(
                        message_id=msg_id,
                        origin_device_id=event.origin_device_id,
                        message=msg,
                        latitude=lat,
                        longitude=lon,
                        severity=severity,
                        status=SOSStatus.ACTIVE,
                        created_at=event.created_at,
                        received_at=now,
                    )
                    db.add(sos_alert)

                elif event.type == OfflineEventType.INCIDENT:
                    title = str(payload.get("title") or payload.get("message") or "Offline Disaster Incident")
                    description = str(payload.get("description") or payload.get("message") or "Reported via offline mesh network")
                    lat = float(payload.get("latitude", 0.0))
                    lon = float(payload.get("longitude", 0.0))
                    type_str = str(payload.get("type", "OTHER")).upper()
                    sev_str = str(payload.get("severity", "MEDIUM")).upper()

                    try:
                        inc_type = IncidentType(type_str)
                    except Exception:
                        inc_type = IncidentType.OTHER

                    try:
                        severity = IncidentSeverity(sev_str)
                    except Exception:
                        severity = IncidentSeverity.MEDIUM

                    media_urls = payload.get("media_urls") or []

                    incident = Incident(
                        message_id=msg_id,
                        title=title[:255],
                        description=description,
                        type=inc_type,
                        latitude=lat,
                        longitude=lon,
                        severity=severity,
                        status=IncidentStatus.REPORTED,
                        created_at=event.created_at,
                        updated_at=now,
                    )
                    incident.media_urls = media_urls
                    db.add(incident)

                elif event.type == OfflineEventType.LOCATION:
                    # Update device location telemetry
                    if event.origin_device_id:
                        origin_dev = db.query(Device).filter(Device.device_id == event.origin_device_id).first()
                        if not origin_dev:
                            origin_dev = Device(
                                device_id=event.origin_device_id,
                                device_type="RELAY",
                                last_seen_at=now,
                                created_at=now
                            )
                            db.add(origin_dev)
                        else:
                            origin_dev.last_seen_at = now

                # Audit in offline_events table
                off_event = OfflineEvent(
                    message_id=msg_id,
                    gateway_id=sync_data.gateway_id,
                    origin_device_id=event.origin_device_id,
                    event_type=event.type,
                    created_at=event.created_at,
                    received_at=now,
                    processed_at=get_utc_now(),
                    status=OfflineEventStatus.PROCESSED,
                )
                off_event.payload = payload
                db.add(off_event)

                db.commit()
                accepted.append(msg_id)

            except Exception as e:
                db.rollback()
                logger.error(f"Error processing offline event {msg_id}: {e}", exc_info=True)
                failed.append(msg_id)

                # Attempt to store failure log
                try:
                    failed_log = OfflineEvent(
                        message_id=msg_id,
                        gateway_id=sync_data.gateway_id,
                        origin_device_id=event.origin_device_id,
                        event_type=event.type,
                        created_at=event.created_at,
                        received_at=now,
                        processed_at=get_utc_now(),
                        status=OfflineEventStatus.FAILED,
                        error_message=str(e),
                    )
                    failed_log.payload = event.payload or {}
                    db.add(failed_log)
                    db.commit()
                except Exception:
                    db.rollback()

        return GatewaySyncResponse(
            success=True,
            accepted=accepted,
            duplicates=duplicates,
            failed=failed
        )
