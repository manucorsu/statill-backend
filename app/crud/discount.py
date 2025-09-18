from sqlalchemy.orm import Session

from ..models.discount import Discount, StatusEnum

from fastapi import HTTPException

from ..schemas.order import *
from datetime import datetime, timezone
from . import store as stores_crud, product as products_crud, sale as sales_crud
from ..schemas.sale import SaleCreate, ProductSale


def get_all(session: Session):
    """
    Retrieves all discounts from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Discount]: A list of all discounts.
    """
    query = session.query(Discount)
    discounts = query.all()
    return discounts


def get_by_id(id: int, session: Session):
    """
    Retrieves a discount by their ID.

    Args:
        id (int): The ID of the discount to retrieve.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        Discount: The discount with the specified ID.
    Raises:
        HTTPException(404): If the discount with the specified ID does not exist.
    """
    discount = session.get(Discount, id)
    if discount is None:
        raise HTTPException(404, detail="Discount not found")

    return discount


def get_all_by_store_id(id: int, session: Session):
    """
    Retrieves all discounts from the database by their store ID.
    Args:
        id (int): The ID of the store.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Discount]: A list for the discounts with the store ID.
    Raises:
        HTTPException(404): If the store with the specified ID does not exist.
    """

    products = session.query(Product).filter(Product.store_id == id).all()
    discounts = session.query(Discount).filter(Discount.product_id in products.id).all()
    return discounts