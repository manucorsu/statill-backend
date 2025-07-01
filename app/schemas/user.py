from pydantic import BaseModel
from typing import Literal
from .general import APIResponse


class UserCreate(BaseModel):
    first_names: str
    last_name: str
    email: str
    password: str
    birthdate: str
    gender: Literal["X", "F", "M"]
    res_area: str

    class Config:
        from_attributes = True


class UserRead(UserCreate):
    id: int
    role: Literal["buyer", "seller", "admin"]
    store_id: int | None
    store_role: Literal["cashier", "owner"] | None

    # Esto se asignar después (role empieza en "buyer")
    # role: Literal["buyer", "seller", "admin"]
    # store_id: int | None
    # store_role: Literal["cashier", "owner"] | None


class GetAllUsersResponse(APIResponse):
    data: list[UserRead]


class GetUserResponse(APIResponse):
    data: UserRead
