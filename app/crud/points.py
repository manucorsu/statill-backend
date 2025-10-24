from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.schemas.sale import SaleCreate, ProductSale

from .user import get_by_id as get_user_by_id
from .store import get_by_id as get_store_by_id

from ..models.points import Points
from ..models.product import Product


from typing import overload, Literal


def points_enabled(store_id: int, session: Session) -> bool:
    """
    Checks if a store has a points system.

    Args:
        store_id (int): The ID of the store to check.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        bool: `True` if the store has a points system, `False` otherwise.
    """
    store = get_store_by_id(store_id, session)
    return store.ps_value is not None and store.ps_value > 0


def get_all_points(session: Session) -> list[Points]:
    """
    Retrieves all points entries from the database.

    Args:
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Points]: A list of all Points entries in the database.
    """
    return session.query(Points).all()


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
        allow_null (bool): If set to `False` (default), a 404 error will be raised if no points entry is found for the given user and store. If set to `True`, the function will silently return `None` instead of raising an error when no entry is found.
    Returns:
        Points|None: The Points entry for the user in the specified store, or `None` if no entry exists and `allow_null` is set to `True`.

    Raises:
        HTTPException(404): If no points entry is found for the given user and store, and `allow_null` is set to `False`.
    """
    user = get_user_by_id(user_id, session)
    store = get_store_by_id(store_id, session)
    if not store.ps_value or store.ps_value <= 0:
        raise HTTPException(status_code=400, detail="Store does not have points system")
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
    if not points_enabled(product.store_id, session) or product.points_price is None:
        raise HTTPException(
            status_code=400, detail="This product cannot be purchased with points"
        )

    points_entry = get_user_points(user_id, product.store_id, session)
    if points_entry.amount < product.points_price:
        raise HTTPException(status_code=400, detail="User does not have enough points")

    from .sale import (
        create as create_sale,
    )  # ningún tipo con un nombre como "Guido van Rossum" me va a prohibir hacer imports cirulares faltando un mes para la entrega

    create_sale(
        sale_data=SaleCreate(
            user_id=user_id,
            store_id=product.store_id,
            products=[
                ProductSale(product_id=product.id, quantity=1)
            ],  # la pésima coding practice
            payment_method=3,
        ),
        session=session,
        using_points=True,
    )
    points_entry.amount -= product.points_price
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
    Raises:
        HTTPException(400): If no products are provided or if the products do not all belong to the same store.
    """
    # ESTA FUNCIÓN NO DEBE TENER ENDPOINT, LO LLAMA CREATE SALE DIRECTAMENTE!!
    if len(products) == 0:
        raise HTTPException(status_code=400, detail="No products provided")
    store_id = int(products[0].store_id)
    if not points_enabled(store_id, session):
        raise HTTPException(400, detail="Store does not have points system")
    user_points = get_user_points(user_id, store_id, session, True)
    assert user_points is None or isinstance(
        user_points, Points
    )  # por qué no podíamos hacerlo en typescript con prisma para no tener que hacer estas cosas marcos t
    if user_points is None:
        user_points = Points(user_id=user_id, store_id=store_id, amount=0)
        session.add(user_points)
        session.commit()
        session.refresh(user_points)
    val = int(get_store_by_id(store_id, session).ps_value)
    points_to_add = 0
    for product in products:
        if product.store_id != store_id:
            raise HTTPException(
                status_code=400, detail="All products must belong to the same store"
            )
        points_to_add += int(product.price / val)
    user_points.amount += points_to_add
    session.commit()
    return


def get_all_by_store_id(id: int, session: Session):
    """
    Retrieves all points from the database by their store ID.
    Args:
        id (int): The ID of the store.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Points]: A list for the points with the store ID.
    Raises:
        HTTPException(404): If the store with the specified ID does not exist.
    """
    points = session.query(Points).filter(Points.store_id == id).all()
    return points
