from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import ObjectDeletedError

from ..models.discount import Discount
from ..schemas.discount import DiscountCreate

from datetime import date

from fastapi import HTTPException

from typing import overload, Literal


def get_all(session: Session):
    """
    Retrieves all discounts from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Discount]: A list of all discounts.
    """
    discounts = session.query(Discount).all()
    return discounts


def get_by_id(id: int, session: Session):
    """
    Retrieves a discount by its ID.

    Args:
        id (int): The ID of the user to retrieve.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        Discount: The discount with the specified ID.
    Raises:
        HTTPException(404): If the discount with the specified ID does not exist.
    """
    discount = session.get(Discount, id)
    if discount is None:
        raise HTTPException(404, "Discount not found")
    return discount


@overload
def get_by_product_id(
    product_id: int, session: Session, raise_404: Literal[True]
) -> Discount: ...

@overload
def get_by_product_id(
    product_id: int, session: Session, raise_404: Literal[False]
) -> Discount | None: ...

def get_by_product_id(
    product_id: int, session: Session, raise_404: bool = True
) -> Discount | None:
    discount = session.query(Discount).filter(Discount.product_id == product_id).first()
    if discount is None and raise_404:
        raise HTTPException(404, f"No discount was found for product {product_id}")
    
    return discount


def create(discount_data: DiscountCreate, session: Session):
    """
    Creates a new discount in the database
    Args:
        discount_data (DiscountCreate): The discount data.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        int: The id of the newly created order.
    """
    discount = Discount(discount_data)
    session.add(discount)
    session.commit()

    session.refresh(discount)
    return int(discount.id)
