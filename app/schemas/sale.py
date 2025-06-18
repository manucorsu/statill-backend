from pydantic import BaseModel
from app.schemas.general import APIResponse


class SaleRead(BaseModel):
    id: int
    user_id: int
    store_id: int
    payement_method: int
    timestamp: str

    class Config:
        from_attributes = True

class ProductSale(BaseModel):
    product_id: int
    quantity: int

class SaleCreate(BaseModel):
    store_id: int
    products: list[ProductSale]
    payment_method: int

    class Config:
        from_attributes = True

class GetAllSalesResponse(APIResponse):
    data: list[SaleRead]

class GetSaleResponse(APIResponse):
    data: SaleRead
