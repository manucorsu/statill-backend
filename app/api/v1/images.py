from __future__ import annotations
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException

from ...dependencies.db import get_db

from typing import Literal

import cloudinary.uploader

import app.crud.user as uc
import app.crud.store as sc
import app.crud.product as pc

from app.schemas.images import CloudinaryUploadData, CloudinaryUploadResponse

from ...models.user import User
from ...models.store import Store
from ...models.product import Product

from ...utils import owns_specified_store

from ..generic_tags import requires_active_user, public

from fastapi.responses import RedirectResponse

from .auth import get_current_user_require_active

name = "images"
router = APIRouter()

CANNOT_SET_ERR = HTTPException(
    403, "You do not have permission to set images for this resource."
)


def __check_image_upload_permissions(obj: User | Store | Product, user: User) -> None:
    checks = {
        User: lambda o, u: o.id == u.id,
        Store: lambda o, u: owns_specified_store(u, o.id),
        Product: lambda o, u: owns_specified_store(u, o.store_id),
    }

    for typ, check in checks.items():
        if isinstance(obj, typ):
            if check(obj, user):
                return
            raise CANNOT_SET_ERR

    raise ValueError(f"Unsupported object type: {type(obj)!r}")


@router.post("/upload", tags=requires_active_user)
def upload_image(
    t: Literal["user", "store", "product"],
    id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user_require_active),
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
    __check_image_upload_permissions(instance, user)
    response = cloudinary.uploader.upload(
        file.file.read(), public_id=f"{t}{id}"
    )  # public_id will be something like 'product203'
    return CloudinaryUploadResponse(
        data=CloudinaryUploadData(
            public_id=response["public_id"],
            url=response["secure_url"],
            format=response["format"],
        ),
        message="Image upload successful",
    )


"""
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
    # __check_image_upload_permissions(
    #     instance,
    # )
"""


@router.get("/id/cloudinary/{cloudinary_public_id}", tags=public)
def get_image_by_cloudinary_id(cloudinary_public_id: str):
    url, _ = cloudinary.utils.cloudinary_url(cloudinary_public_id, secure=True)
    return RedirectResponse(url)


@router.get("/id/object", tags=public)
def get_image_by_object_id(t: Literal["user", "store", "product"], id: int):
    return get_image_by_cloudinary_id(f"{t}{id}")
