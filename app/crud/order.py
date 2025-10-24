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


def create(order_data: OrderCreate, session: Session):
    """
    Creates a new order in the database.
    Args:
        order_data (OrderCreate): The order data to create.
        session (Session): The SQLAlchemy session to use for the insert.
    Returns:
        int: The ID of the newly created order.
    """
    if len(order_data.products) == 0:
        raise HTTPException(
            status_code=400, detail="Order must have at least 1 product"
        )

    stores_crud.get_by_id(
        order_data.store_id, session
    )  # will 404 if the store doesn't exist

    for pd in order_data.products:
        product = products_crud.get_by_id(pd.product_id, session)
        if pd.quantity > product.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough {product.name} in stock",
            )
        if (
            products_crud.get_by_id(pd.product_id, session).store_id
            != order_data.store_id
        ):
            raise HTTPException(
                status_code=400,
                detail=f"Product with id {pd.product_id} does not belong to this store",
            )

    try:
        order = Order(
            store_id=order_data.store_id,
            user_id=order_data.user_id,
            payment_method=order_data.payment_method,
            created_at=datetime.now(timezone.utc),
            status=StatusEnum.PENDING,
        )
        session.add(order)
        session.flush()

        for product_data in order_data.products:
            stmt = (
                select(Product)
                .where(Product.id == product_data.product_id)
                .with_for_update()
            )
            product = session.execute(stmt).scalars().first()
            if (
                product is None
            ):  # por el quilombito que hice arriba, esta y los dos siguientes checks pueden quedar amarillos
                raise HTTPException(
                    status_code=404,
                    detail=f"Product {product_data.product_id} not found",
                )

            if product.store_id != order_data.store_id:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product with id {product_data.product_id} does not belong to this store",
                )

            if product.quantity < product_data.quantity:
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
    except Exception as ex:  # Esto está bien que esté rojo
        session.rollback()
        raise ex


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
