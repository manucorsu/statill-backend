from typing import Literal
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


class ProductRead(BaseModel):
    id: PositiveInt
    store_id: PositiveInt
    name: Annotated[str, Field(min_length=1, pattern=r"\S", max_length=100)]
    brand: Annotated[str, Field(min_length=1, pattern=r"\S", max_length=30)]
    price: Money
    type: UnsignedInt
    quantity: NonNegativeFloat
    desc: NonEmptyStr
    hidden: bool | None
    barcode: NonEmptyStr | None

    @field_validator("price", mode="before")
    @classmethod
    def convert_decimal_to_money(cls, v):
        if isinstance(v, (int, float, Decimal)):
            return Money(value=v)
        return v

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: Annotated[str, Field(min_length=1, pattern=r"\S", max_length=100)]
    brand: Annotated[str, Field(min_length=1, pattern=r"\S", max_length=30)]
    price: Money
    type: PositiveInt
    quantity: NonNegativeFloat
    desc: NonEmptyStr
    barcode: NonEmptyStr | None
    hidden: bool | None = Field(default=False)
    store_id: PositiveInt  # temp until login

    class Config:
        from_attributes = True


class ProductUpdate(BaseModel):
    name: Annotated[str, Field(min_length=1, pattern=r"\S", max_length=100)] | None
    brand: Annotated[str, Field(min_length=1, pattern=r"\S", max_length=30)] | None
    price: Money | None
    type: PositiveInt | None
    quantity: NonNegativeFloat | None
    desc: NonEmptyStr | None
    hidden: bool | None = Field(default=False)
    barcode: NonEmptyStr | None

    class Config:
        from_attributes = True


class GetAllProductsResponse(APIResponse):
    successful: Literal[True]
    data: list[ProductRead]


class GetProductResponse(APIResponse):
    successful: Literal[True]
    data: ProductRead
