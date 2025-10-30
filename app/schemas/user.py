from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Annotated
from .general import APIResponse, SuccessfulResponse
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


class UserUpdate(BaseModel):
    first_names: Annotated[str, Field(min_length=1, max_length=40, pattern=r"\S")]
    last_name: Annotated[str, Field(min_length=1, max_length=40, pattern=r"\S")]
    email: EmailStr
    birthdate: NonEmptyStr
    gender: Literal["X", "F", "M"]
    res_area: Annotated[str, Field(min_length=1, max_length=50, pattern=r"\S")]

    class Config:
        from_attributes = True


class UserRead(BaseModel):
    id: PositiveInt
    first_names: Annotated[str, Field(min_length=1, max_length=40, pattern=r"\S")]
    last_name: Annotated[str, Field(min_length=1, max_length=40, pattern=r"\S")]
    email: EmailStr
    birthdate: NonEmptyStr
    gender: Literal["X", "F", "M"]
    res_area: Annotated[str, Field(min_length=1, max_length=50, pattern=r"\S")]
    store_id: PositiveInt | None
    store_role: Literal["cashier", "owner"] | None

    class Config:
        from_attributes = True


class Token(BaseModel):
    token: str
    token_type: Literal["bearer"] = "bearer"


class GetAllUsersResponse(APIResponse):
    data: list[UserRead]


class GetUserResponse(APIResponse):
    data: UserRead


class LoginResponse(SuccessfulResponse):
    data: Token
