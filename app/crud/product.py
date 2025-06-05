from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


def get_all(session: Session):
    stmt = select(Product)
    return session.execute(stmt)

def get_by_id(id: int, session: Session):
    stmt = select(Product).where(Product.id == id)
    result = session.execute(stmt).scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return result
