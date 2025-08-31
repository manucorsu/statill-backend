from sqlalchemy.orm import Session

from ..models.order import Order, StatusEnum
from ..models.orders_products import OrdersProducts

from fastapi import HTTPException

from ..schemas.order import *
from datetime import datetime, timezone
from . import store as stores_crud, product as products_crud


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
        id (int): The ID of the store.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Order]: A list for the orders with the store ID.
    Raises:
        HTTPException(404): If the store with the specified ID does not exist.
    """
    orders = session.query(Order).filter(Order.store_id == id).all()
    return orders


def get_all_by_user_id(id: int, session: Session):
    """
    Retrieves all orders from the database by their user ID.
    Args:
        id (int): The ID of the user.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Order]: A list for the orders with the user ID.
    Raises:
        HTTPException(404): If the user with the specified ID does not exist.
    """
    orders = session.query(Order).filter(Order.user_id == id).all()
    return orders


def create(order_data: OrderCreate, session: Session):
    """
    Creates a new order in the database.
    Args:
        order_data (OrderCreate): The order data to create.
        session (Session): The SQLAlchemy session to use for the insert.
    Returns:
        int: The ID of the newly created order.
    """
    store = stores_crud.get_by_id(order_data.store_id, session)
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    order = Order(
        store_id=order_data.store_id,
        user_id=order_data.user_id,
        payment_method=order_data.payment_method,
        created_at=datetime.now(timezone.utc),
        received_at=None,
        status=StatusEnum("pending"),
    )
    session.add(order)
    session.commit()

    for product_data in order_data.products:
        product = products_crud.get_by_id(product_data.product_id, session)
        if product.store_id != order_data.store_id:
            raise HTTPException(
                status_code=400,
                detail=f"Product with id {product_data.product_id} does not belong to this store",
            )

        if (product.quantity - product_data.quantity) < 0:
            raise HTTPException(
                status_code=400, detail=f"Not enough {product.name} in stock"
            )

        op = OrdersProducts(
            order_id=order.id,
            product_id=product_data.product_id,
            quantity=product_data.quantity,
        )
        session.add(op)

    session.commit()
    return int(order.id)


def update_status(id: int, session: Session):
    """
    Updates a the status of an order by its ID.
    Args:
        id (int): The ID of the order to update.
        session (Session): The SQLAlchemy session to use for the update.
    Returns:
        None
    Raises:
        HTTPException(404): If the order with the specified ID does not exist.
        HTTPException(400): If the order is already marked "received".
        HTTPException(500): If an order in the database somehow has a status that isn't "pending", "accepted" or "received"
    """
    statuses = [StatusEnum.PENDING, StatusEnum.ACCEPTED, StatusEnum.RECEIVED]
    order = get_by_id(id, session)
    current_status = order.status

    try:
        if current_status == StatusEnum.RECEIVED:
            raise HTTPException(
                400, f"Order already has status {StatusEnum.RECEIVED.value}"
            )

        new_status_index = statuses.index(current_status) + 1
        new_status = statuses[new_status_index]
        order.status = new_status
        if order.status == StatusEnum.RECEIVED:
            order.received_at = datetime.now(timezone.utc)
        session.commit()
        return new_status.value
    except ValueError:
        raise HTTPException(
            500, f"An order in the database has invalid status {current_status}."
        )
