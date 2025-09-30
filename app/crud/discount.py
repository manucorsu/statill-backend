from sqlalchemy.orm import Session

from ..models.discount import Discount
from ..schemas.discount import DiscountCreate, DiscountRead


def _discount_to_discountread(discount: Discount):
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
    return [_discount_to_discountread(d) for d in discounts]


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
