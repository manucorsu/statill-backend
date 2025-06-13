from fastapi import HTTPException
from sqlalchemy import select, insert, delete, update
from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.schemas.general import APIResponse
from app.schemas.sale import SaleCreate
from app.schemas.general import APIResponse

# TODO: ORMizar y terminar

def get_all(session: Session):
    stmt = select(Sale)
    result = session.execute(stmt).scalars().all()
    return result


def get_by_id(id: int, session: Session):
    stmt = select(Sale).where(Sale.id == id)
    result = session.execute(stmt).scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return result

def create(sale: SaleCreate, session: Session):
    stmt = insert(Sale).values(
        **sale.dict(), user_id=1,store_id=2
    )  # este store_id=2 es temporal, queda hasta que hagamos para crear locales
    result = session.execute(stmt)
    session.commit()
    return result