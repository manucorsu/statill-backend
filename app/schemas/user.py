from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Annotated
from .general import APIResponse
from .custom_types import NonEmptyStr, PositiveInt, UserPassword


class UserCreate(BaseModel):
    first_names: Annotated[str, Field(min_length=1, max_length=40, pattern=r"\S")]
    last_name: Annotated[str, Field(min_length=1, max_length=40, pattern=r"\S")]
    email: EmailStr
    password: UserPassword
    birthdate: NonEmptyStr
    gender: Literal["X", "F", "M"]
    res_area: Annotated[str, Field(min_length=1, max_length=50, pattern=r"\S")]

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
