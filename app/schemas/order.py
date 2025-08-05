from pydantic import BaseModel, Field
from app.schemas.general import APIResponse
from typing import Annotated, Literal
from .custom_types import PositiveInt, NonEmptyStr, NonNegativeFloat, Gt0Float


class ProductOrder(BaseModel):
    product_id: PositiveInt
    quantity: Gt0Float


class OrderRead(BaseModel):
    id: PositiveInt
    user_id: PositiveInt | None
    store_id: PositiveInt
    created_at: NonEmptyStr
    status: Literal["pending", "accepted", "received"]
    received_at: NonEmptyStr
    payment_method: Annotated[int, Field(ge=0, le=3)]
    products: list[ProductOrder]

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    store_id: PositiveInt
    products: list[ProductOrder]
    payment_method: Annotated[int, Field(ge=0, le=3)]
    user_id: PositiveInt | None

    class Config:
        from_attributes = True


class GetAllOrdersResponse(APIResponse):
    data: list[OrderRead]


class GetOrderResponse(APIResponse):
    data: OrderRead
