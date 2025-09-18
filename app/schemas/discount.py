from pydantic import BaseModel, Field
from app.schemas.general import APIResponse
from typing import Annotated, Literal
from .custom_types import PositiveInt, NonEmptyStr, NonNegativeFloat, Gt0Float

class DiscountRead(BaseModel):
    id: PositiveInt
    product_id: PositiveInt | None
    type: NonEmptyStr
    pct_off: PositiveInt  | None
    start_date: NonEmptyStr | None
    end_date: NonEmptyStr | None
    days_usable: Annotated[list[bool | None], Field(min_length=7, max_length=7)]
    condition: dict

    class Config:
        from_attributes = True

