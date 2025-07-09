# Custom field types for use in Pydantic schemas

from pydantic import Field
from typing import Annotated
from pydantic import field_validator, BaseModel, ValidationInfo


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

class MoneyAmount(BaseModel):
    value: float

    @field_validator('value')
    def validate_money_amount(cls, v: float, info: ValidationInfo):
        # Ensure value is within range
        if not (0.01 <= v <= 99999999.99):
            raise ValueError("Value must be between 0.01 and 99,999,999.99")
        # Ensure max 2 decimal places
        if round(v, 2) != v:
            raise ValueError("Value must have at most 2 decimal places")
        # Ensure max 10 digits (including decimals)
        digits = len(str(int(v)).replace('-', '')) + 2  # 2 for decimals
        if digits > 10:
            raise ValueError("Value must have at most 10 digits including decimals")
        return v

"""
**Decimal with up to 10 digits and 2 decimal places that is >= 0.01 and <= 99999999.99**
"""

UnsignedInt = Annotated[int, Field(ge=0)]
"""
**An integer that is >= 0.**
"""
