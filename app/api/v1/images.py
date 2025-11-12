from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
from fastapi import APIRouter, File, UploadFile, Depends

from ...dependencies.db import get_db

from typing import Literal

import cloudinary.uploader

import app.crud.user as uc
import app.crud.store as sc
import app.crud.product as pc

from app.schemas.images import CloudinaryUploadData,CloudinaryUploadResponse


name = "images"
router = APIRouter()


@router.post("/upload")
def upload_image(
    t: Literal["user", "store", "product"],
    id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_db),
) -> CloudinaryUploadResponse:
    def type_module():
        match (t):
            case "user":
                return uc
            case "store":
                return sc
            case "product":
                return pc
            case _:
                raise ValueError(f"Invalid type {t}")

    instance = type_module().get_by_id(id, session)

    # TODO : verificar que sea un recurso que pueda acceder el usuario

    response = cloudinary.uploader.upload(
        file.file.read(), folder=t, public_id=f"{t}{id}"
    )  # public_id will be something like 'product203'
    return CloudinaryUploadResponse(
        data=CloudinaryUploadData(
            public_id=response["public_id"],
            url=response["secure_url"],
            format=response["format"]
        )
    )
