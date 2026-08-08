from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.dependencies import get_current_user
from app.core.response import success_response
from app.models.user import User
from app.schemas.user import UserUpdate, UserProfileResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication & Profile"])


@router.get("/me", summary="Get Authenticated User Profile")
def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Returns the authenticated user profile and assigned role (CITIZEN, VOLUNTEER, GOVERNMENT, ADMIN).
    """
    response_data = UserProfileResponse.model_validate(current_user)
    return success_response(data=response_data, message="User profile retrieved successfully")


@router.patch("/me", summary="Update Authenticated User Profile")
def update_my_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Updates the authenticated user's name, phone, or requested role.
    """
    updated_user = AuthService.update_user_profile(db, current_user, update_data)
    response_data = UserProfileResponse.model_validate(updated_user)
    return success_response(data=response_data, message="User profile updated successfully")
