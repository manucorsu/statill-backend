from __future__ import annotations
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from ...crud import discount as crud
from ...schemas.general import APIResponse
from ...schemas.discount import (
    GetAllDiscountsResponse,
    DiscountCreate,
    DiscountRead,
    GetDiscountResponse,
)
from ...dependencies.db import get_db

if TYPE_CHECKING:
    from ...models.discount import Discount

from datetime import date

name = "discounts"
router = APIRouter()


def __discount_to_discountread(discount: Discount):
    return DiscountRead(
        id=discount.id,
        product_id=discount.product_id,
        pct_off=discount.pct_off,
        start_date=str(discount.start_date),
        end_date=str(discount.end_date),
        days_usable=discount.days_usable,
        min_amount=discount.min_amount,
        max_amount=discount.max_amount,
    )


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
    result = [__discount_to_discountread(d) for d in crud.get_all(session)]
    return GetAllDiscountsResponse(
        successful=True, data=result, message="Successfully retrieved all discounts."
    )


@router.get("/{id}", response_model=GetDiscountResponse)
def get_discount_by_id(id: int, session=Depends(get_db)):
    """
    Retrieves a discount by its ID.

    (Will require auth in the future)

    Args:
        id (int): The ID of the discount to retrieve.
        db (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetDiscountResponse: A response containing the discount with the specified ID.

    Raises:
        HTTPException(404): If the discount with the specified ID does not exist.
    """
    discount = crud.get_by_id(id, session)
    return GetDiscountResponse(
        successful=True,
        data=__discount_to_discountread(discount),
        message=f"Successfully retrieved the discount with id {discount.id}",
    )


@router.get("/product/{product_id}")
def get_discount_by_product_id(product_id: int, session=Depends(get_db)):
    """
    Retrieves the discount for the product with the specified id. If that product does not have an active discount, it raises an `HTTPException(404)`.
    """
    discount = crud.get_by_product_id(product_id, session, True)
    return GetDiscountResponse(
        successful=True,
        data=__discount_to_discountread(discount),
        message=f"Successfully retrieved the discount for product {product_id}",
    )


@router.get("/product/{product_id}/allownull")
def get_discount_by_product_id_no_allow_null(product_id: int, session=Depends(get_db)):
    discount = crud.get_by_product_id(product_id, session, False)
    return APIResponse(
        successful=True,
        data=__discount_to_discountread(discount) if discount else None,
        message=f"Successfully retrieved the discount for product {product_id}",
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
        end_date = date.fromisoformat(discount.end_date)

        if start_date < date.today():
            raise HTTPException(
                400, f"Start date ('{start_date}') cannot be in the past."
            )

        if start_date >= end_date:
            raise HTTPException(
                400,
                f"Start date ('{start_date}') should be before end date (f'{end_date}')",
            )

    except ValueError:
        raise HTTPException(
            400,
            f"Invalid format for discount start date or end date (start_date='{discount.start_date}', end_date='{discount.end_date}')",
        )

    # amount check
    if discount.min_amount >= discount.max_amount:
        raise HTTPException(
            400, f"Discount min amount must be smaller than discount max amount."
        )

    # usable days check
    if discount.days_usable == [False, False, False, False, False, False, False]:
        raise HTTPException(400, "The discount must be usable on at least one day.")

    id = crud.create(discount, session)
    return APIResponse(
        successful=True,
        data={"id": id},
        message=f"Successfully created the Discount, which received id {id}.",
    )
