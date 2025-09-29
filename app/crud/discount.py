from sqlalchemy.orm import Session

from ..models.discount import Discount
from ..schemas.discount import DiscountCreate


def get_all(session: Session):
    """
    Retrieves all discounts from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Discount]: A list of all discounts.
    """
    query = session.query(Discount)
    discounts = query.all()
    return discounts


def create(discount_data: DiscountCreate, session: Session):
    """
    Creates a new discount in the database
    Args:
        discount_data (DiscountCreate): The discount data.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        int: The id of the newly created order.
    """
    discount = Discount(**discount_data.model_dump())
    session.add(discount)
    session.commit()
    session.refresh(discount)
    return int(discount.id)
