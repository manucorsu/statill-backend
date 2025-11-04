from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models.user import User

import datetime
from app.models.user import StoreRoleEnum
from fastapi import HTTPException


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def owns_a_store(user: User) -> bool:
    """
    Checks if the user owns a store.

    Args:
        user (User): The user to check.
    Returns:
        bool: True if the user owns a store, False otherwise.
    """
    return (user.store_id is not None) and (user.store_role == StoreRoleEnum.OWNER)


def owns_a_store_raise(user: User):
    """
    Raises an HTTPException if the user does not own a store.

    Args:
        user (User): The user to check.
    Raises:
        HTTPException(403): If the user does not own a store.
    """

    if not owns_a_store(user):
        raise HTTPException(status_code=403, detail="User does not own a store.")
