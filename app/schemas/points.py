from pydantic import BaseModel, Field
from app.schemas.general import SuccessfulResponse
from typing import Annotated, Literal
from .custom_types import PositiveInt, NonEmptyStr, NonNegativeFloat, Gt0Float


class PointsRead(BaseModel):
    id: PositiveInt
    store_id: PositiveInt
    user_id: PositiveInt
    amount: PositiveInt

    class Config:
        from_attributes = True

class PointsSale(BaseModel):  # represents a product being bought with points
    product_id: PositiveInt
    quantity: PositiveInt


class GetAllPointsResponse(SuccessfulResponse):
    data: list[PointsRead]


class GetUserPointsResponse(SuccessfulResponse):
    data: PointsRead
