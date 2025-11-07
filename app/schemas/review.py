from typing import Literal, Optional
from pydantic import BaseModel, field_validator, Field
from app.schemas.general import APIResponse
from .custom_types import (
    PositiveInt,
    NonEmptyStr,
    Money,
    UnsignedInt,
    NonNegativeFloat,
)
from typing import Annotated
from decimal import Decimal


class ReviewRead(BaseModel):
    id: PositiveInt
    store_id: PositiveInt
    user_id: PositiveInt
    stars: PositiveInt
    desc: NonEmptyStr = Annotated[str, Field(min_length=1, max_length=300, pattern=r"\S")]


class GetAllReviewsResponse(APIResponse):
    successful: Literal[True]
    data: list[ReviewRead]


class GetReviewResponse(APIResponse):
    successful: Literal[True]
    data: ReviewRead


class ReviewCreate(BaseModel):
    store_id: PositiveInt
    stars: PositiveInt
    desc: str

    class Config:
        from_attributes = True
