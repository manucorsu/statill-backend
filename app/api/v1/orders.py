from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models.user import User

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.schemas.general import APIResponse
from ...schemas.order import (
    GetAllOrdersResponse,
    GetOrderResponse,
    OrderCreate,
    OrderRead,
    OrderUpdate,
    ProductOrder,
    GetOrderProductsResponse,
)
from ...models.order import Order
from ...dependencies.db import get_db
from ...crud import order as crud

from ..generic_tags import requires_admin, requires_active_user
from .auth import get_current_user_require_admin, get_current_user_require_active
from fastapi import HTTPException
from ...utils import owns_a_store_raise

name = "orders"
router = APIRouter()


def __order_to_orderread(order: Order):
    products_as_schemas: list[ProductOrder] = []
    for op in order.orders_products:
        products_as_schemas.append(ProductOrder(**op.__dict__))

    order_as_dict = order.__dict__
    order_as_dict["products"] = products_as_schemas
    order_as_dict["status"] = str(order.status.value)
    order_as_dict["created_at"] = order.created_at.isoformat()
    order_as_dict["received_at"] = (
        order.received_at.isoformat() if order.received_at else None
    )
    return OrderRead(**order_as_dict)


@router.get("/my", response_model=GetAllOrdersResponse, tags=requires_active_user)
def get_my_orders(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_require_active),
):
    """
    Retrieves all orders for the current authenticated user.

    Args:
        session (Session): The SQLAlchemy session to use for the query.
        current_user (User): The current authenticated active user.
    Returns:
        GetAllOrdersResponse: A response containing a list of all orders for the current user.
    """
    result = crud.get_all_by_user_id(current_user.id, session)
    return GetAllOrdersResponse(
        successful=True,
        data=[__order_to_orderread(o) for o in result],
        message="Successfully retrieved all orders for the current user.",
    )


@router.get("/", response_model=GetAllOrdersResponse, tags=requires_admin)
def get_all_orders(
    session: Session = Depends(get_db),
    _: User = Depends(get_current_user_require_admin),
):
    """
    Retrieves all orders from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.
        _ (User): The current active admin user. Unused, is only there to enforce admin requirement.
    Returns:
        GetAllOrdersResponse: A response containing a list of all orders.
    """
    result = crud.get_all(session)
    return GetAllOrdersResponse(
        successful=True,
        data=[__order_to_orderread(o) for o in result],
        message="Successfully retrieved all orders.",
    )


@router.get("/{id}", response_model=GetOrderResponse, tags=requires_admin)
def get_order_by_id(
    id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user_require_admin),
):
    """
    Retrieves an order by its ID.

    Args:
        id (int): The ID of the order to retrieve.
        db (Session): The SQLAlchemy session to use for the query.
        _ (User): The current authenticated admin user. Unused, is only there to enforce admin requiremebnt.
    Returns:
        GetOrderResponse: A response containing the order with the specified ID.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the order with the specified ID does not exist.
    """
    # import app.crud.user as users_crud
    # order = crud.get_by_id(id, db)
    # if _.id not in [int(i) for i in [order.user_id, users_crud.get_by_id(order.store_id, db).id]]:
    #     raise HTTPException(status_code=403, detail="Not authorized to access this order.")
    result = __order_to_orderread(crud.get_by_id(id, db))
    return GetOrderResponse(
        successful=True,
        data=result,
        message=f"Successfully retrieved the Order with id {result.id}.",
    )


@router.get("/my/store", response_model=GetAllOrdersResponse, tags=requires_active_user)
def get_my_store_orders(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_require_active),
):
    """
    Retrieves all orders for the store owned/managed by the current authenticated user.

    Args:
        session (Session): The SQLAlchemy session to use for the query.
        current_user (User): The current authenticated active user.
    Returns:
        GetAllOrdersResponse: A response containing a list of all orders for the current user's store.
    """
    owns_a_store_raise(current_user, allow_cashiers=True)
    result = crud.get_all_by_store_id(current_user.store_id, session)
    return GetAllOrdersResponse(
        successful=True,
        data=[__order_to_orderread(o) for o in result],
        message="Successfully retrieved all orders for the current user's store.",
    )


@router.get(
    "/store/{store_id}", response_model=GetAllOrdersResponse, tags=requires_admin
)
def get_orders_by_store_id(
    store_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user_require_admin),
):
    """
    Retrieves all orders for a specific store.

    Args:
        store_id (int): The ID of the store to retrieve orders for.
        db (Session): The SQLAlchemy session to use for the query.
        _ (User): The current authenticated admin user. Unused, is only there to enforce admin requirement.

    Returns:
        GetAllOrdersResponse: A response containing all orders for the specified store.
    """
    result = crud.get_all_by_store_id(store_id, db)
    return GetAllOrdersResponse(
        successful=True,
        data=[__order_to_orderread(o) for o in result],
        message=f"Successfully retrieved all Orders for store with id {store_id}.",
    )


@router.get("/user/{user_id}", response_model=GetAllOrdersResponse, tags=requires_admin)
def get_orders_by_user_id(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user_require_admin),
):
    """
    Retrieves all orders for a specific user.

    Args:
        user_id (int): The ID of the user to retrieve orders for.
        db (Session): The SQLAlchemy session to use for the query.
        _ (User): The current authenticated admin user. Unused, is only there to enforce admin requiremebnt.

    Returns:
        GetAllOrdersResponse: A response containing all orders for the specified user.
    """
    result = crud.get_all_by_user_id(user_id, db)
    return GetAllOrdersResponse(
        successful=True,
        data=[__order_to_orderread(o) for o in result],
        message=f"Successfully retrieved all Orders for user with id {user_id}.",
    )


@router.get(
    "/{id}/products", response_model=GetOrderProductsResponse, tags=requires_active_user
)
def get_order_products(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_require_active),
):
    """
    Retrieves all products for a specific order.

    Args:
        id (int): The ID of the order to retrieve products for.
        db (Session): The SQLAlchemy session to use for the query.
        user (User): The current authenticated active user. They must either be the user who placed the order or the owner/cashier of the store the order was placed from.
    Returns:
        GetOrderProductsResponse: A response containing all products for the specified order.
    """
    # Ensure the requesting user is either the one who placed the order,
    # or the owner/cashier of the store the order was placed from.
    order = crud.get_by_id(id, db)
    if order.user_id != user.id:
        # Must be from the same store
        if getattr(user, "store_id", None) != order.store_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this order."
            )
        # And must be owner or cashier of that store
        owns_a_store_raise(user, allow_cashiers=True)
    order = crud.get_by_id(id, db)
    products = [ProductOrder(**op.__dict__) for op in order.orders_products]
    return GetOrderProductsResponse(
        successful=True,
        data=products,
        message=f"Successfully retrieved all Products for order with id {id}.",
    )


@router.post(
    "/", response_model=APIResponse, status_code=201, tags=requires_active_user
)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_require_active),
):
    """
    Creates an order.

    Args:
        sale (OrderCreate): The order data.
        db (Session): The SQLAlchemy session to use for the query.
        user (User): The current authenticated active user.
    Returns:
        APIResponse: A response containing the ID of the created order.
    """
    order_id = crud.create(order, db, user)
    return APIResponse(
        successful=True,
        data={"id": order_id},
        message=f"Successfully created the Order, which received id {order_id}.",
    )


@router.patch("/{id}/status", response_model=APIResponse, tags=requires_active_user)
def update_order_status(
    id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_require_active),
):
    """
    Updates the status of an order by its ID.

    Args:
        id (int): The ID of the order to update.
        db (Session): The SQLAlchemy session to use for the update.
        user (User): The current authenticated active user. They must be an owner/cashier of the store the order was placed from.

    Returns:
        APIResponse: A response indicating the success of the update operation.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the order with the specified ID does not exist.
    """
    order = crud.get_by_id(id, db)
    owns_a_store_raise(user, allow_cashiers=True)

    if getattr(user, "store_id", None) != order.store_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this order."
        )
    #  must be owner or cashier of that store
    crud.update_status(id, db)
    return APIResponse(
        successful=True,
        data=None,
        message="Successfully updated the Order's status.",
    )


@router.patch("/{id}/products", response_model=APIResponse, tags=requires_active_user)
def update_order_products(
    id: int,
    updates: OrderUpdate,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user_require_active),
):
    """
    Updates the products of an order by its ID.

    Args:
        id (int): The ID of the order to update.
        updates (OrderUpdate): The order updates.
        session (Session): The SQLAlchemy session to use for the update.
        user (User): The current authenticated active user. They must be the user who placed the order.

    Args:
        updates (OrderUpdate): The order updates.
        session (Session): The SQLAlchemy session to use for the update.

    Returns:
        APIResponse: A response indicating the success of the update operation.

    Raises:
        HTTPException(400): If the order's status was not 'pending'.
        HTTPException(404): If the order with the specified ID does not exist.
    """
    order = crud.get_by_id(id, session)
    if order.user_id != user.id:
        raise HTTPException(
            403, "Only the user who placed the order can update its products."
        )
    crud.update_products(id, updates, session)
    return APIResponse(
        successful=True, data=None, message="Successfully updated the Order's products."
    )


@router.patch("/{id}/cancel", response_model=APIResponse, tags=requires_active_user)
def cancel_order(
    id: int,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user_require_active),
):
    # Ensure the requesting user is either the one who placed the order,
    # or the owner/cashier of the store the order was placed from.
    order = crud.get_by_id(id, session)
    if order.user_id != user.id:
        # Must be from the same store
        if getattr(user, "store_id", None) != order.store_id:
            raise HTTPException(
                status_code=403, detail="Not authorized to access this order."
            )
        # And must be owner or cashier of that store
        owns_a_store_raise(user, allow_cashiers=True)
    crud.cancel(id, session)
    return APIResponse(
        successful=True, data=None, message="Successfully cancelled the order"
    )
