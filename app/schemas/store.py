from time import timezone
from typing import Literal
from pydantic import BaseModel
from app.schemas.general import APIResponse
from datetime import time

class StoreRead(BaseModel):
    id: int
    name: str
    address: str
    category: int
    preorder_enabled: bool
    ps_enabled: bool
    days_open: list[bool]
    opening_times: list[time]
    closing_times: list[time]
    payment_methods: list[bool]

    class Config:
        from_attributes = True


class StoreCreate(BaseModel):
    name: str
    address: str
    category: int
    preorder_enabled: bool
    ps_enabled: bool
    days_open: list[bool]
    opening_times: list[time]
    closing_times: list[time]
    payment_methods: list[bool]
    class Config:
        from_attributes = True


class GetAllStoresResponse(APIResponse):
    successful: Literal[True]
    data: list[StoreRead]


class GetStoreResponse(APIResponse):
    data: StoreRead