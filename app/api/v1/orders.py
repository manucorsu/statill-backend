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
)
from ...models.order import Order
from ...dependencies.db import get_db
from ...crud import order as crud

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


@router.get("/", response_model=GetAllOrdersResponse)
def get_all_orders(session: Session = Depends(get_db)):
    """
    Retrieves all orders from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetAllOrdersResponse: A response containing a list of all orders.

    """
    result = crud.get_all(session)
    return GetAllOrdersResponse(
        successful=True,
        data=[__order_to_orderread(o) for o in result],
        message="Successfully retrieved all orders.",
    )


@router.get("/{id}", response_model=GetOrderResponse)
def get_order_by_id(id: int, db: Session = Depends(get_db)):
    """
    Retrieves an order by its ID.

    (Will require auth in the future)

    Args:
        **id (int): The ID of the order to retrieve.**
        db (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetOrderResponse: A response containing the order with the specified ID.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the order with the specified ID does not exist.
    """
    result = __order_to_orderread(crud.get_by_id(id, db))
    return GetOrderResponse(
        successful=True,
        data=result,
        message=f"Successfully retrieved the Order with id {result.id}.",
    )


@router.get("/store/{store_id}", response_model=GetAllOrdersResponse)
def get_orders_by_store_id(store_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all orders for a specific store.

    (Will require auth in the future)

    Args:
        store_id (int): The ID of the store to retrieve orders for.
        db (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetAllOrdersResponse: A response containing all orders for the specified store.
    """
    result = crud.get_all_by_store_id(store_id, db)
    return GetAllOrdersResponse(
        successful=True,
        data=[__order_to_orderread(o) for o in result],
        message=f"Successfully retrieved all Orders for store with id {store_id}.",
    )


@router.get("/user/{user_id}", response_model=GetAllOrdersResponse)
def get_orders_by_user_id(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieves all orders for a specific user.

    (Will require auth in the future)

    Args:
        user_id (int): The ID of the user to retrieve orders for.
        db (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetAllOrdersResponse: A response containing all orders for the specified user.
    """
    result = crud.get_all_by_user_id(user_id, db)
    return GetAllOrdersResponse(
        successful=True,
        data=[__order_to_orderread(o) for o in result],
        message=f"Successfully retrieved all Orders for user with id {user_id}.",
    )


@router.post("/", response_model=APIResponse, status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """
    Creates an order.

    (Will require auth in the future)

    Args:
        sale (OrderCreate): The order data.
        db (Session): The SQLAlchemy session to use for the query.
    """
    order_id = crud.create(order, db)
    return APIResponse(
        successful=True,
        data={"id": order_id},
        message=f"Successfully created the Order, which received id {order_id}.",
    )


@router.patch("/{id}/status", response_model=APIResponse)
def update_order_status(id: int, db: Session = Depends(get_db)):
    """
    Updates the status of an order by its ID.

    (Will require auth in the future)

    Args:
        id (int): The ID of the order to update.
        db (Session): The SQLAlchemy session to use for the update.

    Returns:
        APIResponse: A response indicating the success of the update operation.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the order with the specified ID does not exist.
    """
    crud.update_status(id, db)
    return APIResponse(
        successful=True,
        data=None,
        message="Successfully updated the Order's status.",
    )


@router.patch("/{id}/products", response_model=APIResponse)
def update_order_products(
    id: int, updates: OrderUpdate, session: Session = Depends(get_db)
):
    """
    Updates the products of an order by its ID.

    (Will require auth in the future)

    Args:
        id (int): The ID of the order to update.
        updates (OrderUpdate): The order updates.
        session (Session): The SQLAlchemy session to use for the update.

    Args:
        updates (OrderUpdate): The order updates.
        session (Session): The SQLAlchemy session to use for the update.

    Returns:
        APIResponse: A response indicating the success of the update operation.

    Raises:
        HTTPException(400): If the order's status was not 'pending'.
        HTTPException(404): If the order with the specified ID does not exist.
    """
    crud.update_order_products(id, updates, session)
    return APIResponse(
        successful=True, data=None, message="Successfully updated the Order's products."
    )


@router.patch("/{id}/cancel", response_model=APIResponse)
def cancel_order(id: int, session: Session = Depends(get_db)):
    crud.cancel(id, session)
    return APIResponse(
        successful=True, data=None, message="Successfully cancelled the order"
    )
