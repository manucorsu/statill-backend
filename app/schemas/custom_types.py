# Custom field types for use in Pydantic schemas

from pydantic import Field
from typing import Annotated


PositiveInt = Annotated[int, Field(ge=1)]
"""
**An integer that is >= 1.**
"""

NonNegativeFloat = Annotated[float, Field(ge=0)]
"""
**A number (float) that is >= 0.**
"""

NonEmptyStr = Annotated[str, Field(min_length=1, pattern=r"\S")]
"""
**A string that is not empty and not only whitespace.**
"""

UserPassword = Annotated[str, Field(min_length=8)]
"""
**A string that is at least 8 characters long.**

This type should only be used on creation, as responses should always 
return hashes and not plain-text passwords.
"""

MoneyAmount = Annotated[
    float, Field(ge=0.01, le=99999999.99, max_digits=10, decimal_places=2)
]
"""
**Decimal with up to 10 digits and 2 decimal places that is >= 0.01 and <= 99999999.99**
"""

UnsignedInt = Annotated[int, Field(ge=0)]
"""
**An integer that is >= 0.**
"""
