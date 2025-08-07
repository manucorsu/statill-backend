from sqlalchemy.orm import Session, object_mapper

from ..models.order import Order

from fastapi import HTTPException

from ..schemas.order import *
from datetime import date
from email_validator import validate_email, EmailNotValidError
from typing import overload, Literal
from . import store as stores_crud


def get_all(session: Session):
    """
    Retrieves all orders from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Order]: A list of all orders.
    """
    query = session.query(Order)
    orders = query.all()
    return orders


def get_by_id(id: int, session: Session):
    """
    Retrieves an order by their ID.

    Args:
        id (int): The ID of the order to retrieve.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        Order: The order with the specified ID.
    Raises:
        HTTPException(404): If the order with the specified ID does not exist.
    """
    order = session.get(Order, id)
    if order is None:
        raise HTTPException(404, detail="Order not found")

    return order


def get_all_by_store_id(id: int, session: Session):
    """
    Retrieves all orders from the database by their store ID.
    Args:
        id (int): The ID of the order.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Order]: A list for the orders with the order ID.
    Raises:
        HTTPException(404): If the order with the specified ID does not exist.
    """
    orders = session.query(Order).filter(Order.store_id == id).all()
    return orders
