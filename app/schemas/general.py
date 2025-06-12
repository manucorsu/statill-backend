from typing import Any, Optional
from pydantic import BaseModel
import warnings


class Message(BaseModel):
    message: str

    def __init__(self, *args, **kwargs):
        warnings.warn("Please use APIResponse instead.", DeprecationWarning)


class APIResponse(BaseModel):
    successful: bool
    data: Optional[Any]
    message: str
