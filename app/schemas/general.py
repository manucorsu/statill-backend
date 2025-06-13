from typing import Any, Optional
from pydantic import BaseModel
from typing_extensions import deprecated

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
    message: str
