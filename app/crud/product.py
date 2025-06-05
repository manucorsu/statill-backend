from fastapi import HTTPException
from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate


def get_all(session: Session):
    stmt = select(Product)
    return session.execute(stmt)


def get_by_id(id: int, session: Session):
    stmt = select(Product).where(Product.id == id)
    result = session.execute(stmt).scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return result


def create(product: ProductCreate, session: Session):
    # temporal: hasta que hagamos stores CRUD
    values = product.dict()
    values["store_id"] = 1
    #
    stmt = insert(Product).values(**product.dict())
    result = session.execute(stmt)
    session.commit()
    return result
