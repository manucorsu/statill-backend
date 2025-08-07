from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.schemas.general import APIResponse
from ...schemas.order import GetAllOrdersResponse, GetOrderResponse, OrderCreate
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
        successful=True, data=result, message="Successfully retrieved all orders."
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
    order = crud.get_by_id(id, db)
    result = crud.get_by_id(id, db)
    return GetOrderResponse(
        successful=True,
        data=result,
        message=f"Successfully retrieved the Order with id {result.id}.",
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
    order_id = crud.create_order(order, db)
    return APIResponse(
        successful=True,
        data={"id": order_id},
        message=f"Successfully created the Order, which received id {order_id}.",
    )