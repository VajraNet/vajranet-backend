from fastapi import APIRouter, Depends, status
from app.core.dependencies import get_current_user
from app.core.response import success_response
from app.models.user import User
from app.schemas.media import CloudinarySignatureRequest, CloudinarySignatureResponse
from app.services.media_service import MediaService

router = APIRouter(prefix="/media", tags=["Media & Attachments"])


@router.post("/signature", summary="Generate Cloudinary Direct Upload Signature", status_code=status.HTTP_200_OK)
def get_media_upload_signature(
    request_data: CloudinarySignatureRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generates a secure cryptographic signature allowing the frontend client to upload
    disaster images/videos directly to Cloudinary without burdening the FastAPI backend server.
    """
    signature_data = MediaService.generate_upload_signature(request_data)
    return success_response(
        data=signature_data,
        message="Cloudinary upload signature generated successfully"
    )
