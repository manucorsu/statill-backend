from sqlalchemy.orm import Session

from ..models.discount import Discount

from fastapi import HTTPException

from ..schemas.order import *
from datetime import datetime, timezone
from . import store as stores_crud, product as products_crud, sale as sales_crud
from ..schemas.sale import SaleCreate, ProductSale


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
