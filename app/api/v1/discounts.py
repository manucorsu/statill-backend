from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from ...crud import discount as crud
from ...schemas.general import APIResponse
from ...schemas.discount import GetAllDiscountsResponse, DiscountCreate
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


@router.post("/", response_model=APIResponse)
def create_discount(discount: DiscountCreate, session=Depends(get_db)):
    """
    Creates a discount.

    Args:
        discount (DiscountCreate): The discount data.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        (APIResponse) An APIResponse containing the new discount's id.
    """
    # TODO URGENTE AGREGAR LOS CHECKS QUE FALTAN!
    id = crud.create(discount, session)
    return APIResponse(
        successful=True,
        data={"id": id},
        message=f"Successfully created the Discount, which received id {id}.",
    )
