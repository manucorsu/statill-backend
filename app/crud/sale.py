from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.products_sales import ProductsSales

from app.models.sale import Sale
from app.models.store import Store
from app.schemas.sale import SaleCreate

from . import product as products_crud
from . import store as stores_crud

def get_all(session: Session):
    """
    Retrieves all sales from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Sale]: A list of all sales.
    """
    return session.query(Sale).all()

def get_ps_by_sale(sale: Sale, session: Session):
    return session.query(ProductsSales).filter(ProductsSales.product_id==sale.id)

def get_by_id(id: int, session: Session):
    """
    Retrieves a sale by its ID.
    Args:
        id (int): The ID of the sale to retrieve.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        Sale: The sale with the specified ID.
    Raises:
        HTTPException(404): If the sale with the specified ID does not exist.
    """
    sale = session.get(Sale, id)
    if sale is None:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale

    


def create_sale_with_products(sale_data: SaleCreate, session: Session):
    """
    Creates a new sale in the database.
    Args:
        sale_data (SaleCreate): The sale data to create.
        session (Session): The SQLAlchemy session to use for the insert.
    Returns:
        int: The ID of the newly created sale.
    """
    store = stores_crud.get_by_id(sale_data.store_id, session)
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    sale = Sale(
        store_id=sale_data.store_id,
        user_id=sale_data.user_id,
        payment_method=sale_data.payment_method,
        timestamp=datetime.now(),
    )
    session.add(sale)
    session.commit()

    for product_data in sale_data.products:
        product = products_crud.get_by_id(product_data.product_id, session)
        if (product.store_id != sale_data.store_id):
            raise HTTPException(status_code=400, detail=f"Product with id {product_data.product_id} does not belong to this store")
    
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
