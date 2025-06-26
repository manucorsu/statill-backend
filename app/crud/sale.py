from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.products_sales import ProductsSales

from app.models.sale import Sale
from app.models.store import Store
from app.schemas.sale import SaleCreate

from . import product as products_crud

def get_all(session: Session):
    return session.query(Sale).all()


def get_by_id(id: int, session: Session):
    sale = session.get(Sale, id)
    if sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale

def create(sale_data: SaleCreate, session: Session):
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

    for product_data in sale_data.products:
        product = products_crud.get_by_id(product_data.product_id, session)
        if (product.store_id != sale_data.store_id):
            raise HTTPException(status_code=400, detail=f"Product with id {product_data.product_id} not found on this store")
    
        if ((product.quantity - product_data.quantity) < 0):
            raise HTTPException(status_code=400, detail=f"Not enough {product.name} in stock")
        else:
            product.quantity -= product_data.quantity

        ps = ProductsSales(
            sale_id=sale.id, product_id=product_data.product_id, quantity=product_data.quantity
        )
        session.add(ps)

    session.refresh(sale)
    session.commit()
    return int(sale.id)
