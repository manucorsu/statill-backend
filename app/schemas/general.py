from typing import Any, Optional, Literal
from pydantic import BaseModel
from typing_extensions import deprecated
from .custom_types import NonEmptyStr


@deprecated("Please use APIResponse instead.")
class Message(BaseModel):
    message: str


class APIResponse(BaseModel):
    """
    A generic, standard API response model to be used as the base for all API responses.
    Attributes:
        successful (bool): Indicates whether the API call was successful.
        data (Optional[Any]): The data returned by the API, if any (will mostly be `dict[str, any]`, `list[dict[str, any]]`, or `None`).
        message (str): A message providing additional information about the API call.
    """

    successful: bool
    data: Optional[Any]
    message: NonEmptyStr


class SuccessfulResponse(APIResponse):
    """
    A generic, standard API response model for successful responses. Inherits from `APIResponse` and ensures `successful` is always `True`.
    Attributes:
        successful (Literal[True]): Always `True` to indicate a successful API call.
        data (Optional[Any]): The data returned by the API, if any (will mostly be `dict[str, any]`, `list[dict[str, any]]`, or `None`).
        message (str): A message providing additional information about the API call.
    """

    # no sé como es que tardamos hasta el once de octubre para que alguien se le occurra esto
    successful: Literal[True] = True
