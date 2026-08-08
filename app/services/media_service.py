import time
import hashlib
from app.core.config import settings
from app.schemas.media import CloudinarySignatureRequest, CloudinarySignatureResponse


class MediaService:
    @staticmethod
    def generate_upload_signature(request: CloudinarySignatureRequest) -> CloudinarySignatureResponse:
        timestamp = int(time.time())
        cloud_name = settings.CLOUDINARY_CLOUD_NAME or "demo"
        api_key = settings.CLOUDINARY_API_KEY or "123456789012345"
        api_secret = settings.CLOUDINARY_API_SECRET or "mock_secret"

        # Cloudinary expects parameters sorted alphabetically
        tags_str = ",".join(sorted(request.tags or ["disaster_evidence"]))
        params_to_sign = f"folder={request.folder}&tags={tags_str}&timestamp={timestamp}{api_secret}"
        
        signature = hashlib.sha1(params_to_sign.encode("utf-8")).hexdigest()

        upload_url = f"https://api.cloudinary.com/v1_1/{cloud_name}/{request.resource_type}/upload"

        return CloudinarySignatureResponse(
            timestamp=timestamp,
            signature=signature,
            api_key=api_key,
            cloud_name=cloud_name,
            upload_url=upload_url,
            folder=request.folder
        )
