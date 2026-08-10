import logging
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.config import settings
from app.schemas.ai import AIChatRequest, AIChatResponse
from app.services.announcement_service import AnnouncementService
from app.services.resource_service import ResourceService
from app.models.sos import SOSAlert, SOSStatus, SOSSeverity
from app.models.incident import Incident, IncidentStatus
from app.models.shelter import Shelter, ShelterStatus
from app.models.hospital import Hospital
from app.models.volunteer import VolunteerTask, TaskStatus

logger = logging.getLogger(__name__)


class AIService:
    @staticmethod
    def handle_emergency_chat(request: AIChatRequest, db: Session) -> AIChatResponse:
        """
        Disaster AI Assistant with strict human-in-the-loop safety guardrails.
        Assists across 3 key personas:
        - Citizens: Natural disaster safety guidance, shelter routing, official announcements.
        - Government EOC: Situational data analysis (e.g. highest SOS alert areas, alert distribution).
        - Volunteers: Operational guidance (e.g. nearby incidents requiring response, open tasks).
        
        STRICT SAFETY NOTICE:
        - VajraAI assists human decision-makers and NEVER makes independent medical diagnoses,
          critical rescue determinations, or autonomous dispatch decisions.
        """
        query = request.message.lower().strip()

        # Fetch active announcements to inject ground-truth context
        active_announcements = AnnouncementService.get_active_announcements(db)

        # ---------------------------------------------------------
        # 1. GOVERNMENT / SITUATIONAL AWARENESS QUERIES
        # ---------------------------------------------------------
        if any(k in query for k in ["highest number of sos", "sos alert", "sos stats", "highest sos", "alert distribution", "emergency overview"]):
            active_sos_count = db.query(SOSAlert).filter(SOSAlert.status == SOSStatus.ACTIVE).count()
            critical_sos_count = db.query(SOSAlert).filter(
                SOSAlert.status == SOSStatus.ACTIVE,
                SOSAlert.severity == SOSSeverity.CRITICAL
            ).count()
            total_incidents = db.query(Incident).filter(Incident.status.in_([IncidentStatus.REPORTED, IncidentStatus.VERIFIED])).count()
            
            # Find clusters / sample locations
            recent_sos = db.query(SOSAlert).filter(SOSAlert.status == SOSStatus.ACTIVE).order_by(SOSAlert.created_at.desc()).limit(5).all()
            loc_summary = ", ".join([f"Lat {s.latitude:.2f}/Lon {s.longitude:.2f} ({s.severity.value})" for s in recent_sos[:3]]) if recent_sos else "No active SOS clusters"

            reply = (
                f"Situational Awareness Summary: Currently tracking {active_sos_count} active SOS alerts "
                f"({critical_sos_count} CRITICAL priority) and {total_incidents} ongoing disaster incidents. "
                f"Active distress hotspots include: {loc_summary}. "
                f"Commanders can coordinate rescue deployments and dispatch verified response teams via the Government Dashboard."
            )
            suggested = [
                "Filter CRITICAL SOS alerts on map",
                "Publish area evacuation announcement",
                "Review open rescue incidents"
            ]

        # ---------------------------------------------------------
        # 2. VOLUNTEER / OPERATIONAL ASSISTANCE QUERIES
        # ---------------------------------------------------------
        elif any(k in query for k in ["requiring assistance", "incidents requiring", "volunteer task", "field task", "how can i help", "open task"]):
            open_incidents = db.query(Incident).filter(
                Incident.status.in_([IncidentStatus.REPORTED, IncidentStatus.VERIFIED])
            ).order_by(Incident.created_at.desc()).limit(3).all()

            if open_incidents:
                inc_list = "; ".join([f"'{inc.title}' ({inc.severity.value} priority at {inc.latitude:.2f}, {inc.longitude:.2f})" for inc in open_incidents])
                reply = (
                    f"Operational Guidance for Responders: {len(open_incidents)} incidents currently require field assistance: {inc_list}. "
                    f"Volunteers can claim tasks directly on the Incident Response Board and report on-ground progress."
                )
            else:
                reply = (
                    "Operational Guidance for Responders: All reported incidents are currently assigned or resolved. "
                    "Check the Volunteer Portal for newly incoming field tasks, private shelter registrations, and relief supply missions."
                )
            suggested = [
                "View claimable incident response tasks",
                "Register private emergency shelter",
                "Check relief distribution center needs"
            ]

        # ---------------------------------------------------------
        # 3. CITIZEN SAFETY GUIDANCE: FLOODS
        # ---------------------------------------------------------
        elif "flood" in query or "water" in query:
            reply = (
                "Flood Safety Advisory: Move to higher ground immediately. Do not attempt to walk, swim, or drive "
                "through floodwaters (turn around, don't drown). Avoid downed power lines and electrical wires. "
                "Monitor official VajraNet government emergency broadcasts for evacuation routes."
            )
            suggested = ["Find nearby high-ground shelters", "Trigger SOS if trapped", "Check government announcements"]

        # ---------------------------------------------------------
        # 4. CITIZEN SAFETY GUIDANCE: EARTHQUAKES
        # ---------------------------------------------------------
        elif "earthquake" in query or "quake" in query or "shake" in query:
            reply = (
                "Earthquake Safety Advisory: DROP, COVER, and HOLD ON. If indoors, stay away from windows and heavy furniture. "
                "If outdoors, move to an open area away from power lines and collapsing structures. "
                "After shaking stops, evacuate calmly and check for gas leaks before using matches or electricity."
            )
            suggested = ["Locate open ground shelters", "Report building damage incident", "Check hospital bed availability"]

        # ---------------------------------------------------------
        # 5. CITIZEN SAFETY GUIDANCE: FIRE
        # ---------------------------------------------------------
        elif "fire" in query or "smoke" in query:
            reply = (
                "Fire Safety Advisory: Evacuate the premises immediately. Stay low under smoke. Feel doors with the back "
                "of your hand before opening. Never use elevators during a fire evacuation. "
                "Once safe outside, stay outside and report your location to emergency authorities."
            )
            suggested = ["Submit incident report with location", "Find nearby medical centers", "Trigger SOS if trapped"]

        # ---------------------------------------------------------
        # 6. CITIZEN SAFETY GUIDANCE: CYCLONE / STORM
        # ---------------------------------------------------------
        elif "cyclone" in query or "storm" in query or "hurricane" in query or "wind" in query:
            reply = (
                "Cyclone & Severe Storm Advisory: Stay indoors in the strongest part of the building away from glass windows. "
                "Disconnect electrical appliances and keep emergency flashlights accessible. "
                "Do not venture outside during the eye of the storm. Follow official evacuation alerts if issued."
            )
            suggested = ["Find nearest reinforced shelter", "Check official storm announcements", "Trigger SOS if in danger"]

        # ---------------------------------------------------------
        # 7. RESOURCE INQUIRIES: SHELTERS, HOSPITALS, RELIEF
        # ---------------------------------------------------------
        elif "shelter" in query or "hospital" in query or "relief" in query or "bed" in query or "icu" in query:
            nearby_shelters = []
            if request.latitude is not None and request.longitude is not None:
                nearby_shelters = ResourceService.get_nearby_shelters(db, request.latitude, request.longitude, radius_km=20.0)
            
            if nearby_shelters:
                top_shelter = nearby_shelters[0]
                reply = (
                    f"Nearest verified emergency shelter: {top_shelter.name} located at {top_shelter.address} "
                    f"({top_shelter.distance_km} km away). Capacity status: {top_shelter.status.value}. "
                    f"Please navigate safely using main arterial routes."
                )
            else:
                reply = (
                    "You can view verified open shelters, hospitals with live bed counts, and relief distribution centers "
                    "directly in the VajraNet Nearby Resources tab."
                )
            suggested = ["View nearby shelters list", "View nearby hospitals with ICU beds", "Find food & water relief centers"]

        # ---------------------------------------------------------
        # 8. DEFAULT / GENERAL DISASTER ASSISTANCE
        # ---------------------------------------------------------
        else:
            if active_announcements:
                reply = (
                    f"Current Emergency Broadcast: {active_announcements[0].title}. {active_announcements[0].content} "
                    f"Please stay in safe designated zones and monitor official instructions."
                )
            else:
                reply = (
                    "VajraNet Emergency Information: Stay alert, follow official instructions from local authorities, "
                    "and keep battery on emergency devices conserved. If you or someone nearby is in immediate life danger, "
                    "use the SOS button immediately."
                )
            suggested = ["Submit SOS Alert", "Report Disaster Incident", "View Safety Announcements"]

        safety_advisory = (
            "NOTICE: VajraAI assists human decision-makers by interpreting operational data and safety guidelines. "
            "It does not perform medical diagnosis, dispatch emergency vehicles directly, or replace human first responders."
        )

        return AIChatResponse(
            reply=reply,
            safety_advisory=safety_advisory,
            suggested_actions=suggested,
            active_announcements_count=len(active_announcements)
        )

