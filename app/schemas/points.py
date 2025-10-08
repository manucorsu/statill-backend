from pydantic import BaseModel, Field
from app.schemas.general import APIResponse
from typing import Annotated, Literal
from .custom_types import PositiveInt, NonEmptyStr, NonNegativeFloat, Gt0Float


class PointsRead(BaseModel):
    id: PositiveInt
    store_id: PositiveInt
    user_id: PositiveInt
    amount: PositiveInt

    class Config:
        from_attributes = True


class CreatePointsWithSale(BaseModel):
    products: list[PositiveInt]
    user_id: PositiveInt
