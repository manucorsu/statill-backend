from sqlalchemy.orm import Session
from fastapi import HTTPException

from .user import get_by_id as get_user_by_id
from .store import get_by_id as get_store_by_id

from ..models.points import Points
from ..models.product import Product

from typing import overload, Literal


@overload
def get_user_points(
    user_id: int, store_id: int, session: Session, allow_null: Literal[True]
) -> Points | None: ...


@overload
def get_user_points(
    user_id: int, store_id: int, session: Session, allow_null: Literal[False] = False
) -> Points: ...


def get_user_points(
    user_id: int, store_id: int, session: Session, allow_null: bool = False
) -> Points | None:
    """
    Retrieves the user's points in the specified store.

    Args:
        user_id (int): The ID of the user.
        store_id (int): The ID of the store.
        session (Session): The SQLAlchemy session to use for the query.
        allow_null (bool): If set to `False` (default), a 404 error will be raised if no points entry is found for the given user and store. If set to `True`, the function will return `None` instead of raising an error when no entry is found.
    Returns:
        Points|None: The Points entry for the user in the specified store, or `None` if no entry exists and `allow_null` is set to `True`.

    Raises:
        HTTPException(404): If no points entry is found for the given user and store, and `allow_null` is set to `False`.
    """
    user = get_user_by_id(user_id, session)
    store = get_store_by_id(store_id, session)
    points_entry = (
        session.query(Points)
        .filter(Points.user_id == user.id, Points.store_id == store.id)
        .first()
    )
    if not points_entry and not allow_null:
        raise HTTPException(status_code=404, detail="Points entry not found")
    return points_entry


def buy_with_points(user_id: int, product: Product, session: Session):
    """
    Deducts points from a user when they purchase a product using points.

    Args:
        user_id (int): The ID of the user making the purchase.
        product (Product): The product being purchased.
        session (Session): The SQLAlchemy session to use for the query.
    Raises:
        HTTPException(400): If the product does not have a points price or if the user does not have enough points to make the purchase.
    """
    if product.points_price is None:
        raise HTTPException(
            status_code=400, detail="This product cannot be purchased with points"
        )
    points_entry = get_user_points(user_id, product.store_id, session)
    if points_entry is None or points_entry.amount < product.points_price:
        raise HTTPException(status_code=400, detail="User does not have enough points")
    points_entry.points -= product.points_price
    session.add(points_entry)
    session.commit()


def gain_points_from_purchase(user_id: int, products: list[Product], session: Session):
    """
    Adds points to a user's account based on the products they have purchased.

    Args:
        user_id (int): The ID of the user making the purchase.
        products (list[Product]): The list of products being purchased.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        None
    """
    if len(products) == 0:
        raise HTTPException(status_code=400, detail="No products provided")

    store_id = int(products[0].store_id)
    user_points = get_user_points(user_id, store_id, session, False)
    val = int(get_store_by_id(store_id, session).ps_value)
    points_to_add = 0
    for product in products:
        if product.store_id != products[0].store_id:
            raise HTTPException(
                status_code=400, detail="All products must belong to the same store"
            )
        points_to_add += int(product.price / val)
    user_points.amount += points_to_add
    session.commit()
    return int(user_points.amount)
