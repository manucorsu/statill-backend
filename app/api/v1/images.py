from fastapi import APIRouter, File, UploadFile
from ...main import app
from typing import Literal
import cloudinary.uploader



name = "images"
router = APIRouter()

@app.post("/upload")
def upload_image(t: Literal["user","store","product"],id:int, file:UploadFile=File(...)):
    upload = cloudinary.uploader.upload(file.file.read(), folder=t,)