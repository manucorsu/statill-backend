from pydantic import BaseModel, Field
from app.schemas.general import APIResponse
from typing import Annotated
from .custom_types import PositiveInt, NonEmptyStr, NonNegativeFloat, Gt0Float


class SaleRead(BaseModel):
    id: PositiveInt
    user_id: PositiveInt
    store_id: PositiveInt
    payment_method: Annotated[int, Field(ge=0, le=3)]
    timestamp: NonEmptyStr

    class Config:
        from_attributes = True


class ProductSale(BaseModel):
    product_id: PositiveInt
    quantity: Gt0Float


class SaleCreate(BaseModel):
    store_id: PositiveInt
    products: list[ProductSale]
    payment_method: Annotated[int, Field(ge=0, le=3)]
    user_id: PositiveInt

    class Config:
        from_attributes = True


class GetAllSalesResponse(APIResponse):
    data: list[SaleRead]


class GetSaleResponse(APIResponse):
    data: SaleRead
