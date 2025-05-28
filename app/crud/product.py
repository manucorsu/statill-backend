from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


def get_all(session: Session):
    stmt = select(Product)
    return session.execute(stmt)
