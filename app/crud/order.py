from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.user import User
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from ..models.order import Order, StatusEnum
from ..models.orders_products import OrdersProducts
from ..models.product import Product

from fastapi import HTTPException

from ..schemas.order import *
from datetime import datetime, timezone
from . import store as stores_crud, product as products_crud, sale as sales_crud
from ..schemas.sale import SaleCreate, ProductSale


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


def get_order_products(id: int, session: Session):
    """
    Retrieves all products associated with an order by the order ID.
    Args:
        id (int): The ID of the order.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[OrdersProducts]: A list of products associated with the order.
    Raises:
        HTTPException(404): If the order with the specified ID does not exist.
    """
    order = get_by_id(id, session)
    return order.orders_products


def create(order_data: OrderCreate, session: Session, user: User) -> int:
    """
    Creates a new order in the database.
    Args:
        order_data (OrderCreate): The order data to create.
        session (Session): The SQLAlchemy session to use for the insert.
    Returns:
        int: The ID of the newly created order.
    """
    if not order_data.products:
        raise HTTPException(400, "Order must have at least 1 product")

    # Ensure store exists (will 404 internally)
    stores_crud.get_by_id(order_data.store_id, session)

    product_ids = [p.product_id for p in order_data.products]

    try:
        # Lock all involved products in a single query
        stmt = (
            select(Product)
            .where(Product.id.in_(product_ids))
            .with_for_update()
        )
        db_products = session.execute(stmt).scalars().all()

        # Build dictionary for fast access
        product_map = {p.id: p for p in db_products}

        # Validate: all products exist
        missing = set(product_ids) - set(product_map.keys())
        if missing:
            raise HTTPException(
                404,
                f"Products not found: {', '.join(map(str, missing))}"
            )

        # Validate each product BEFORE creating the order
        for item in order_data.products:
            product = product_map[item.product_id]

            if product.store_id != order_data.store_id:
                raise HTTPException(
                    400,
                    f"Product {product.id} does not belong to this store"
                )

            if product.quantity < item.quantity:
                raise HTTPException(
                    400,
                    f"Not enough {product.name} in stock"
                )

        # Create order first
        order = Order(
            store_id=order_data.store_id,
            user_id=user.id,
            payment_method=order_data.payment_method,
            created_at=datetime.now(timezone.utc),
            status=StatusEnum.PENDING,
        )
        session.add(order)
        session.flush()  # order.id now available

        # Create order-product rows
        for item in order_data.products:
            session.add(
                OrdersProducts(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                )
            )

            # Deduct stock
            product_map[item.product_id].quantity -= item.quantity

        session.commit()
        return int(order.id)

    except Exception:
        session.rollback()
        raise


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

        if new_status == StatusEnum.RECEIVED:  # puede quedar amarillo
            sales_crud.create(
                SaleCreate(
                    store_id=order.store_id,
                    products=[
                        ProductSale(**ps.__dict__) for ps in order.orders_products
                    ],
                    payment_method=order.payment_method,
                    user_id=order.user_id,
                ),
                session,
            )
            order.received_at = datetime.now(timezone.utc)

        order.status = new_status
        session.commit()
        return new_status.value
    except ValueError:
        if (
            current_status == StatusEnum.CANCELLED
        ):  # para el que mire el coverage: Que esto esté amarillo ESTÁ BIEN, si no hay algo muy pero muy mal
            raise HTTPException(400, "Cancelled orders cannot be updated.")
        else:
            raise HTTPException(  # para el que mire el coverage: Que esto esté rojo ESTÁ BIEN, si no hay algo muy pero muy mal
                500, f"An order in the database has invalid status {current_status}."
            )


def update_products(id: int, updates: OrderUpdate, session: Session):
    """
    Updates the products associated with an order.
    Args:
        id (int): The ID of the order to update.
        updates (OrderUpdate): An object containing the list of products to update.
        session (Session): The SQLAlchemy session used for database operations.

    Raises:
        HTTPException(404): If the order with the specified ID does not exist.
        HTTPException(400): If the order has no products.
        HTTPException(400): If the order is not pending.
        HTTPException(400): If a product does not belong to the store.
        HTTPException(400): If there is insufficient stock for a product.
    """
    order = get_by_id(id, session)
    if order.status != StatusEnum.PENDING:
        raise HTTPException(400, "Only pending orders can be updated.")
    if len(updates.products) == 0:
        raise HTTPException(
            status_code=400, detail="Order must have at least 1 product"
        )
    try:
        for old_op in order.orders_products:  # este for puede quedar amarillo
            session.delete(old_op)

        for product_data in updates.products:
            stmt = (
                select(Product)
                .where(Product.id == product_data.product_id)
                .with_for_update()
            )
            product = session.execute(stmt).scalars().first()
            if product is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product {product_data.product_id} not found",
                )

            if product.store_id != order.store_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product with id {product_data.product_id} does not belong to this store",
                )

            if product.quantity < product_data.quantity:
                raise HTTPException(
                    status_code=400, detail=f"Not enough {product.name} in stock"
                )

            old_op = OrdersProducts(
                order_id=order.id,
                product_id=product_data.product_id,
                quantity=product_data.quantity,
            )
            session.add(old_op)

            session.commit()
            return
    except Exception as ex:  # Esto está bien que esté rojo
        session.rollback()
        raise ex


def cancel(id: int, session: Session):
    order = get_by_id(id, session)
    if order.status == StatusEnum.RECEIVED:
        raise HTTPException(400, "Received orders cannot be cancelled.")

    order.status = StatusEnum.CANCELLED
    session.commit()

    # todo: notificar al usuario por mail
