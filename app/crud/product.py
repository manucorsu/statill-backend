from app.dependencies.db import get_db
from app.models.product import Product
from sqlalchemy import select

session = get_db()


def get_all(session):
    """
    Returns all products in the database as a `ScalarResult` of `Product` instances.

    Args:
        None

    Returns:
        ScalarResult: A scalar result containing all the products in the database as `Product` instances
    """
    return session.scalars(select(Product))
