from pydantic import BaseModel, Field
from app.schemas.general import APIResponse
from typing import Annotated, Literal, Optional
from .custom_types import PositiveInt, NonEmptyStr, NonNegativeFloat, Gt0Float
from ..models.discount import INTEGER_MAX_VALUE


class DiscountRead(BaseModel):
    id: PositiveInt
    product_id: PositiveInt
    pct_off: Annotated[int, Field(ge=1, le=100)]
    start_date: NonEmptyStr
    end_date: NonEmptyStr
    days_usable: Annotated[list[bool | None], Field(min_length=7, max_length=7)]
    min_amount: Annotated[int, Field(ge=1, le=INTEGER_MAX_VALUE)] = 1
    max_amount: Annotated[int, Field(ge=1, le=INTEGER_MAX_VALUE)] = (
        INTEGER_MAX_VALUE  # estos dos después se chequean para ver que max no sea < min
    )

    class Config:
        from_attributes = True


class DiscountCreate(BaseModel):
    product_id: PositiveInt
    pct_off: Annotated[int, Field(ge=1, le=100)]
    start_date: NonEmptyStr
    end_date: NonEmptyStr
    days_usable: Annotated[list[bool | None], Field(min_length=7, max_length=7)]
    min_amount: PositiveInt = 1
    max_amount: PositiveInt = INTEGER_MAX_VALUE


class GetAllDiscountsResponse(APIResponse):
    data: list[DiscountRead]
