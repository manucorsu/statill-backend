from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from ...schemas.order import GetAllOrdersResponse
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
