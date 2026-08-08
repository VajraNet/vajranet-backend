from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.core.response import success_response
from app.models.user import User
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/citizen", tags=["Citizen Operations"])


@router.get("/overview", summary="Get Citizen Emergency Dashboard Overview")
def get_citizen_overview(
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0, description="Optional user latitude for nearby counts"),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0, description="Optional user longitude for nearby counts"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns an aggregated overview for citizens:
    - User's active SOS alert
    - User's reported disaster incidents
    - Nearby shelters and hospitals count
    - Active government emergency announcements
    """
    overview_data = DashboardService.get_citizen_overview(db, current_user, latitude, longitude)
    return success_response(data=overview_data, message="Citizen overview retrieved successfully")
