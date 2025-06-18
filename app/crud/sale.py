from fastapi import HTTPException
from sqlalchemy import select, insert, delete, update
from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.schemas.sale import SaleCreate

def get_all(session: Session):
    return session.query(Sale).all()


def get_by_id(id: int, session: Session):
    sale = session.get(Sale, id)
    if product is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return product

def create(sale_data: SaleCreate, session: Session):
    sale = Sale(
        **sale_data.model_dump(), store_id=2
    )  # este store_id=2 es temporal, queda hasta que hagamos para crear locales
    session.add(sale)
    session.commit()
    session.refresh(sale)
    return sale.id

def update_by_id(id: int, sale_data: SaleCreate, session: Session):
    sale = get_by_id(id, session)
    
    updates = sale_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(sale, field, value)

    session.commit()

def delete_by_id(id: int, session:Session):
    item = get_by_id(id, session)
    session.execute(delete(Sale).where(Sale.id == item.id))
    session.commit()