from pydantic import BaseModel, EmailStr
from typing import Literal
from .general import APIResponse
from .custom_types import NonEmptyStr, PositiveInt, UserPassword


class UserCreate(BaseModel):
    first_names: NonEmptyStr
    last_name: NonEmptyStr
    email: NonEmptyStr
    password: UserPassword
    birthdate: NonEmptyStr
    gender: Literal["X", "F", "M"]
    res_area: NonEmptyStr

    class Config:
        from_attributes = True


class UserRead(UserCreate):
    id: PositiveInt
    store_id: PositiveInt | None
    store_role: Literal["cashier", "owner"] | None


class GetAllUsersResponse(APIResponse):
    data: list[UserRead]


class GetUserResponse(APIResponse):
    data: UserRead
