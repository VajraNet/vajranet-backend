from typing import Optional, List
from pydantic import BaseModel, Field


class CloudinarySignatureRequest(BaseModel):
    folder: str = Field(default="vajranet/incidents", description="Target Cloudinary folder")
    resource_type: str = Field(default="image", description="image, video, or auto")
    tags: Optional[List[str]] = Field(default_factory=lambda: ["disaster_evidence"])


class CloudinarySignatureResponse(BaseModel):
    timestamp: int
    signature: str
    api_key: str
    cloud_name: str
    upload_url: str
    folder: str
