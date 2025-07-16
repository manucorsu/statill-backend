# Custom field types for use in Pydantic schemas

from pydantic import Field
from typing import Annotated, Any
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from decimal import Decimal, ROUND_HALF_UP


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


class Money:
    """
    A number that's 0.01 <= value <= 99,999,999.99 rounded half-up to two decimals. **It should only be used as a Pydantic schema field type.**
    """

    def __init__(self, value: float):
        self.value = float(
            Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )

    def __float__(self):
        return self.value

    def __repr__(self):
        return f"{self.value:.2f}"

    def __eq__(self, other):
        return float(self) == float(other)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type, _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.float_schema(),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda v: v.value
            ),
        )

    @classmethod
    def _validate(cls, v: Any) -> "Money":
        try:
            value = float(v)
        except (ValueError, TypeError):
            raise ValueError("Money value must be a number")

        if not (0.01 <= value <= 99_999_999.99):
            raise ValueError("Money value must be between 0.01 and 99,999,999.99")

        return cls(value)


UnsignedInt = Annotated[int, Field(ge=0)]
"""
**An integer that is >= 0.**
"""

Gt0Float = Annotated[float, Field(gt=0)]
"""
**A float that is > 0.**
"""
