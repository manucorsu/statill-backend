from pydantic import BaseModel, HttpUrl
from ..schemas.general import SuccessfulResponse


class CloudinaryUploadData(BaseModel):
    public_id: str
    url: HttpUrl
    format: str


class CloudinaryUploadResponse(SuccessfulResponse):
    data: CloudinaryUploadData


class GetCloudinaryURLResponse(SuccessfulResponse):
    data: HttpUrl
