from pydantic import BaseModel
from typing import Literal


class UserCreate:
    first_names: str
    last_name: str
    email: str
    password: str
    birthdate: str
    gender: Literal["X", "F", "M"]
    res_area: str
    role: Literal["buyer", "seller", "admin"]
    store_id: int | None
    store_role: Literal["cashier", "owner"] | None
