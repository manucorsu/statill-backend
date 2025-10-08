from sqlalchemy.orm import Session

from ..models.discount import Discount
from ..schemas.discount import DiscountCreate, DiscountRead

from datetime import date

from fastapi import HTTPException


def get_all(session: Session) -> list[Discount]:
    """
    Retrieves all discounts from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Discount]: A list of all discounts.
    """
    did_cleanup = False
    discounts = session.query(Discount).all()
    result: list[Discount] = []
    for d in discounts:
        if date.today() > d.end_date:
            print(
                f"Deleting discount {d.id} because it has expired"
            )  # No encontré la forma de que fastapi-cli no me rompa logging
            session.delete(d)
            did_cleanup = True
        else:
            result.append(d)

    if did_cleanup:
        session.commit()
        return get_all(session)

    return result


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
