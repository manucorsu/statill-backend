from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from ...crud import discount as crud
from ...schemas.general import APIResponse
from ...schemas.discount import GetAllDiscountsResponse, DiscountCreate
from ...dependencies.db import get_db

from datetime import date

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
    # date checks
    try:
        start_date = date.fromisoformat(discount.start_date)
        end_date = date.fromisoformat(discount.start_date)

        if start_date >= end_date:
            raise HTTPException(400, "Start date should be before end date")
    except ValueError:
        raise HTTPException(
            400,
            f"Invalid format for discount start date or end date (start_date={discount.start_date}, end_date={discount.end_date})",
        )

    # amount checks
    if discount.min_amount >= discount.max_amount:
        raise HTTPException(
            400, f"Discount min amount must be smaller than discount max amount."
        )

    # days usable checks
    if discount.days_usable == [False, False, False, False, False, False, False]:
        raise HTTPException(400, "The discount must be usable on at least one day.")

    id = crud.create(discount, session)
    return APIResponse(
        successful=True,
        data={"id": id},
        message=f"Successfully created the Discount, which received id {id}.",
    )
