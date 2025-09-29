from pydantic import BaseModel, Field
from app.schemas.general import APIResponse
from typing import Annotated, Literal, Optional
from .custom_types import PositiveInt, NonEmptyStr, NonNegativeFloat, Gt0Float
from ..models.discount import INTEGER_MAX_VALUE


class DiscountRead(BaseModel):
    id: PositiveInt
    product_id: PositiveInt
    type: NonEmptyStr
    pct_off: PositiveInt
    start_date: NonEmptyStr
    end_date: NonEmptyStr
    days_usable: Annotated[list[bool | None], Field(min_length=7, max_length=7)]
    min_amount: PositiveInt = 1
    max_amount: PositiveInt = INTEGER_MAX_VALUE

    class Config:
        from_attributes = True


class GetAllDiscountsResponse(APIResponse):
    data: list[DiscountRead]
