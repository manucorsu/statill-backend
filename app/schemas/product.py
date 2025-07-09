from typing import Literal
from pydantic import BaseModel
from app.schemas.general import APIResponse
from .custom_types import (
    PositiveInt,
    NonEmptyStr,
    MoneyAmount,
    UnsignedInt,
    NonNegativeFloat,
)


class ProductRead(BaseModel):
    id: PositiveInt
    store_id: PositiveInt
    name: NonEmptyStr
    brand: NonEmptyStr
    price: MoneyAmount
    type: UnsignedInt
    quantity: NonNegativeFloat
    desc: NonEmptyStr
    barcode: NonEmptyStr | None

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: NonEmptyStr
    brand: NonEmptyStr
    price: MoneyAmount
    type: UnsignedInt
    quantity: NonNegativeFloat
    desc: NonEmptyStr
    barcode: NonEmptyStr | None

    class Config:
        from_attributes = True


class GetAllProductsResponse(APIResponse):
    successful: Literal[True]
    data: list[ProductRead]


class GetProductResponse(APIResponse):
    data: ProductRead
