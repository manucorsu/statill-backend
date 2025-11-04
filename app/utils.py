from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models.user import User

import datetime
from app.models.user import StoreRoleEnum
from fastapi import HTTPException


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


def owns_a_store(user: User, allow_cashiers: bool = False) -> bool:
    """
    Checks if the user owns a store.

    Args:
        user (User): The user to check.
        allow_cashiers (bool): Whether to consider cashiers as store owners.
    Returns:
        bool: True if the user owns a store, False otherwise.
    """
    return (user.store_id is not None) and (
        user.store_role == StoreRoleEnum.OWNER
        or (allow_cashiers and user.store_role == StoreRoleEnum.CASHIER)
    )


def owns_a_store_raise(user: User, allow_cashiers: bool = False):
    """
    Raises an HTTPException if the user does not own a store.

    Args:
        user (User): The user to check.
        allow_cashiers (bool): Whether to consider cashiers as store owners.
    Raises:
        HTTPException(403): If the user does not own a store.
    """

    if not owns_a_store(user, allow_cashiers=allow_cashiers):
        raise HTTPException(status_code=403, detail="User does not own a store.")


def owns_specified_store(user: User, store_id: int) -> bool:
    """
    Checks if the user owns the specified store.

    Args:
        user (User): The user to check.
        store_id (int): The ID of the store to check.
    Returns:
        bool: True if the user owns the specified store, False otherwise.
    """
    return (user.store_id == store_id) and (user.store_role == StoreRoleEnum.OWNER)


def owns_specified_store_raise(user: User, store_id: int):
    """
    Raises an HTTPException if the user does not own the specified store.

    Args:
        user (User): The user to check.
        store_id (int): The ID of the store to check.
    Raises:
        HTTPException(403): If the user does not own the specified store.
    """

    if not owns_specified_store(user, store_id):
        raise HTTPException(
            status_code=403, detail="User does not own the specified store."
        )
