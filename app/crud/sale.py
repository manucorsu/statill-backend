from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.products_sales import ProductsSales

from app.models.sale import Sale
from app.models.store import Store
from app.schemas.sale import SaleCreate

from . import product as products_crud

# from . import store as stores_crud


def get_all(session: Session):
    """
    Retrieves all sales from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Sale]: A list of all sales.
    """
    return session.query(Sale).all()


def get_ps_by_sale(sale: Sale, session: Session):
    return session.query(ProductsSales).filter(ProductsSales.sale_id == sale.id).all()


def get_by_id(id: int, session: Session):
    """
    Retrieves a sale by its ID.
    Args:
        id (int): The ID of the sale to retrieve.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        Sale: The sale with the specified ID.
    Raises:
        HTTPException(404): If the sale with the specified ID does not exist.
    """
    sale = session.get(Sale, id)
    if sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


def get_sales_by_user_id(user_id: int, session: Session):
    return session.query(Sale).filter(Sale.user_id == user_id).all()


def create(sale_data: SaleCreate, session: Session, using_points: bool = False) -> int:
    """
    Creates a new sale in the database.
    Args:
        sale_data (SaleCreate): The sale data to create.
        session (Session): The SQLAlchemy session to use for the insert.
        using_points (bool): Whether the user is using points to pay for ALL of the products in this sale. Defaults to `False`.
    Returns:
        int: The ID of the newly created sale.
    """
    print(sale_data, "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
    if using_points and sale_data.user_id is None:
        raise HTTPException(
            status_code=400, detail="Anonymous users cannot use points to pay for sales"
        )
    import app.crud.user as users_crud

    if sale_data.user_id != None:
        users_crud.get_by_id(sale_data.user_id, session)  # raises 404 if not found
    sale = Sale(
        store_id=sale_data.store_id,  # me di cuenta de que no hace falta pero es mucho quilombo sacarlo :)
        user_id=sale_data.user_id,  # (can be None)
        payment_method=sale_data.payment_method,
        timestamp=datetime.now(timezone.utc),
    )
    session.add(sale)
    session.commit()

    products_model_instances: list[Product] = []  # ver if not using_points...
    for product_data in sale_data.products:
        product = products_crud.get_by_id(product_data.product_id, session)
        if product.store_id != sale_data.store_id:
            raise HTTPException(
                status_code=400,
                detail=f"Product with id {product_data.product_id} does not belong to this store",
            )

        if (product.quantity - product_data.quantity) < 0:
            raise HTTPException(
                status_code=400, detail=f"Not enough {product.name} in stock"
            )
        else:
            product.quantity -= product_data.quantity

        ps = ProductsSales(
            sale_id=sale.id,
            product_id=product_data.product_id,
            quantity=product_data.quantity,
        )
        session.add(ps)
        products_model_instances.append(product)
    session.refresh(sale)
    from .points import gain_points_from_purchase, points_enabled

    if not using_points and points_enabled(sale.store_id, session):
        gain_points_from_purchase(sale_data.user_id, products_model_instances, session)

    session.commit()
    return int(sale.id)


def get_by_store_id(store_id: int, session: Session):
    """
    Retrieves all sales from the database by their store ID.
    Args:
        store_id (int): The ID of the store.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Sale]: A list for the sales with the store ID.
    Raises:
        HTTPException(404): If the store with the specified ID does not exist.
    """
    sales = session.query(Sale).filter(Sale.store_id == store_id)
    return sales.all()


def get_all_by_store_owner(store_owner: User, session: Session):
    """
    Retrieves all sales for the store owned by the specified user.
    Args:
        store_owner (User): The user who owns the store.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Sale]: A list of all sales for the store owned by the user.
    Raises:
        HTTPException(404): If the store owned by the user does not exist.
    """
    import app.crud.store as stores_crud

    store_id = stores_crud.get_by_id(store_owner.store_id, session).id
    return get_by_store_id(store_id, session)
