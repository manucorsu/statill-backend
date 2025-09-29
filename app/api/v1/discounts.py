from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from ...crud import discount as crud
from ...schemas.discount import GetAllDiscountsResponse
from ...dependencies.db import get_db

name = "discounts"
router = APIRouter()


@router.get("/", response_model=GetAllDiscountsResponse)
def get_all_discounts(session: Session = Depends(get_db)):
    """
    Retrieves all discount data from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetAllDiscountsResponse: A response containing a list of all orders.

    (Will require auth in the future)
    (Will require admin role in the future)
    """
    result = crud.get_all(session)
    return GetAllDiscountsResponse(
        successful=True, data=result, message="Successfully retrieved all discounts."
    )
