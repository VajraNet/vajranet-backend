from fastapi import APIRouter
from app.api.v1 import (
    auth, citizen, sos, incidents, shelters,
    hospitals, relief_centers, announcements,
    government, volunteers, gateway, devices,
    media, ai, resources, emergency_contacts,
    trusted_devices
)

api_router = APIRouter(prefix="/api/v1")

# Mount domain routers
api_router.include_router(auth.router)
api_router.include_router(citizen.router)
api_router.include_router(sos.router)
api_router.include_router(incidents.router)
api_router.include_router(shelters.router)
api_router.include_router(hospitals.router)
api_router.include_router(relief_centers.router)
api_router.include_router(announcements.router)
api_router.include_router(government.router)
api_router.include_router(volunteers.router)
api_router.include_router(gateway.router)
api_router.include_router(devices.router)
api_router.include_router(media.router)
api_router.include_router(ai.router)
api_router.include_router(resources.router)
api_router.include_router(emergency_contacts.router)
api_router.include_router(trusted_devices.router)
