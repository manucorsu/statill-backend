from typing import Literal, Annotated
from pydantic import BaseModel, Field
from app.schemas.general import APIResponse
from datetime import time
from .custom_types import PositiveInt, NonEmptyStr, UnsignedInt


class StoreRead(BaseModel):
    id: PositiveInt
    name: NonEmptyStr
    address: NonEmptyStr
    category: UnsignedInt
    preorder_enabled: bool
    ps_enabled: bool
    opening_times: Annotated[list[time | None], Field(min_length=7, max_length=7)]
    closing_times: Annotated[list[time | None], Field(min_length=7, max_length=7)]
    payment_methods: Annotated[list[bool], Field(min_length=4, max_length=4)]

    class Config:
        from_attributes = True


class StoreCreate(BaseModel):
    name: NonEmptyStr
    address: NonEmptyStr
    category: UnsignedInt
    preorder_enabled: bool
    ps_enabled: bool
    opening_times: Annotated[list[time | None], Field(min_length=7, max_length=7)]
    closing_times: Annotated[list[time | None], Field(min_length=7, max_length=7)]
    payment_methods: Annotated[list[bool], Field(min_length=4, max_length=4)]

    class Config:
        from_attributes = True


class GetAllStoresResponse(APIResponse):
    successful: Literal[True]
    data: list[StoreRead]


class GetStoreResponse(APIResponse):
    data: StoreRead
