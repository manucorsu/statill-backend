from typing import Literal
from pydantic import BaseModel
from app.schemas.general import APIResponse


class ProductRead(BaseModel):
    id: int
    store_id: int
    name: str
    brand: str
    price: float
    type: int
    quantity: int
    desc: str
    barcode: str | None

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    brand: str
    price: float
    type: int
    quantity: int
    desc: str
    barcode: str | None

    class Config:
        from_attributes = True


class GetAllProductsResponse(APIResponse):
    successful: Literal[True]
    data: list[ProductRead]


class GetProductResponse(APIResponse):
    data: ProductRead
