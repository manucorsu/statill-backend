from pydantic import BaseModel


class ProductRead(BaseModel):
    id: int
    store_id: int
    name: str
    brand: str
    price: float
    type: int
    quantity: int
    desc: str

    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    name: str
    brand: str
    price: float
    type: int
    quantity: int
    desc: str

    class Config:
        from_attributes = True