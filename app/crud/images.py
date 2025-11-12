from pydantic import BaseModel
from ..schemas.general import SuccessfulResponse
class FileUploadData(BaseModel):
    public_id:str
    url:str
    format:str

class UploadFile(SuccessfulResponse):
    data:FileUploadData