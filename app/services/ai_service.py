import logging
from typing import List
from sqlalchemy.orm import Session
from app.core.config import settings
from app.schemas.ai import AIChatRequest, AIChatResponse
from app.services.announcement_service import AnnouncementService
from app.services.resource_service import ResourceService

logger = logging.getLogger(__name__)


class AIService:
    @staticmethod
    def handle_emergency_chat(request: AIChatRequest, db: Session) -> AIChatResponse:
        """
        Disaster AI Assistant with strict safety guardrails.
        Answers questions based on active government announcements and verified emergency guidelines.
        Never triages medical emergencies or simulates emergency dispatch.
        """
        query = request.message.lower().strip()

        # Fetch active announcements to inject ground-truth context
        active_announcements = AnnouncementService.get_active_announcements(db)
        announcements_text = "\n".join([f"- {a.title}: {a.content}" for a in active_announcements[:3]])

        # 1. Flood guidance
        if "flood" in query or "water" in query:
            reply = (
                "Flood Safety Advisory: Move to higher ground immediately. Do not attempt to walk, swim, or drive "
                "through floodwaters (turn around, don't drown). Avoid downed power lines and electrical wires. "
                "Monitor official VajraNet government emergency broadcasts for evacuation routes."
            )
            suggested = ["Find nearby high-ground shelters", "Trigger SOS if trapped", "Check government announcements"]

        # 2. Earthquake guidance
        elif "earthquake" in query or "quake" in query or "shake" in query:
            reply = (
                "Earthquake Safety Advisory: DROP, COVER, and HOLD ON. If indoors, stay away from windows and heavy furniture. "
                "If outdoors, move to an open area away from power lines and collapsing structures. "
                "After shaking stops, evacuate calmly and check for gas leaks before using matches or electricity."
            )
            suggested = ["Locate open ground shelters", "Report building damage incident", "Check hospital bed availability"]

        # 3. Fire guidance
        elif "fire" in query or "smoke" in query:
            reply = (
                "Fire Safety Advisory: Evacuate the premises immediately. Stay low under smoke. Feel doors with the back "
                "of your hand before opening. Never use elevators during a fire evacuation. "
                "Once safe outside, stay outside and report your location to emergency authorities."
            )
            suggested = ["Submit incident report with location", "Find nearby medical centers", "Trigger SOS if trapped"]

        # 4. Shelters / Hospitals inquiry
        elif "shelter" in query or "hospital" in query or "relief" in query or "bed" in query:
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

        # 5. General / Default disaster assistance
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
            "NOTICE: This AI assistant provides safety information and official updates only. "
            "It does not perform medical diagnosis, dispatch emergency vehicles directly, or replace human first responders."
        )

        return AIChatResponse(
            reply=reply,
            safety_advisory=safety_advisory,
            suggested_actions=suggested,
            active_announcements_count=len(active_announcements)
        )
