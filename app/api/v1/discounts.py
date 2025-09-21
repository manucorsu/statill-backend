from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.schemas.general import APIResponse
from ...schemas.discount import DiscountRead
from ...models.order import Order
from ...dependencies.db import get_db
from ...crud import order as crud

router = APIRouter()


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
