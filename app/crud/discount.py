from sqlalchemy.orm import Session

from ..models.discount import Discount
from ..schemas.discount import DiscountCreate, DiscountRead
from datetime import date
import logging


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


def get_all(session: Session) -> list[DiscountRead]:
    """
    Retrieves all discounts from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Discount]: A list of all discounts.
    """
    did_cleanup = False
    query = session.query(Discount)
    discounts = query.all()
    result: list[DiscountRead] = []
    for d in discounts:
        if date.today() > d.end_date:
            logging.info(f"Deleting discount {d.id} because it is expired")
            session.delete(d)
            did_cleanup = True
        else:
            result.append(_discount_to_discountread(d))

    if did_cleanup:
        session.commit()
        return get_all(session)

    return result


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
