from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import select, insert, delete, update
from sqlalchemy.orm import Session
from app.models.products_sales import ProductsSales

from app.models.sale import Sale
from app.models.store import Store
from app.schemas.sale import SaleCreate

def get_all(session: Session):
    return session.query(Sale).all()


def get_by_id(id: int, session: Session):
    sale = session.get(Sale, id)
    if sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale

def update_by_id(id: int, sale_data: SaleCreate, session: Session):
    sale = get_by_id(id, session)

    updates = sale_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(sale, field, value)

    session.commit()


def delete_by_id(id: int, session: Session):
    item = get_by_id(id, session)
    session.execute(delete(Sale).where(Sale.id == item.id))
    session.commit()


def create_sale_with_products(sale_data: SaleCreate, session: Session):
    store = session.get(Store, sale_data.store_id) # TODO: Cambiar por la función de crud.store cuando exista
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    sale = Sale(
        store_id=sale_data.store_id,
        user_id=1,
        payment_method=sale_data.payment_method,
        timestamp=datetime.now(),
    )
    session.add(sale)
    session.commit()

    for p in sale_data.products:
        ps = ProductsSales(
            sale_id=sale.id, product_id=p.product_id, quantity=p.quantity
        )
        session.add(ps)

    session.refresh(sale)
    session.commit()
    return sale.id
