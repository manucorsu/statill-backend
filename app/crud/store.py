from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.products_sales import ProductsSales

from app.models.store import Store
from app.schemas.store import StoreCreate

from . import product as products_crud

def get_all(session: Session):
    """
    Retrieves all stores from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Store]: A list of all stores.
    """
    return session.query(Store).all()

def get_by_id(id: int, session: Session):
    """
    Retrieves a store by its ID.
    Args:
        id (int): The ID of the store to retrieve.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        Store: The store with the specified ID.
    Raises:
        HTTPException(404): If the store with the specified ID does not exist.
    """
    store = session.get(Store, id)
    if store is None:
        raise HTTPException(status_code=404, detail="Store not found")
    return store

def create(store_data: StoreCreate, session: Session):
    """
    Creates a new store in the database.
    Args:
        store_data (StoreCreate): The store data to create.
        session (Session): The SQLAlchemy session to use for the insert.
    Returns:
        int: The ID of the newly created store.
    """
    store = Store(
        **store_data.model_dump()
    ) 
    session.add(store)
    session.commit()
    session.refresh(store)
    return store.id

def update(id: int, store_data: StoreCreate, session: Session):
    """
    Updates a store by its ID.
    Args:
        id (int): The ID of the store to update.
        store_data (StoreCreate): The updated store data.
        session (Session): The SQLAlchemy session to use for the update.
    Returns:
        None
    Raises:
        HTTPException(404): If the store with the specified ID does not exist.
    """
    store = get_by_id(id, session)

    updates = store_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(store, field, value)

    session.commit()

def delete(id: int, session: Session):
    """
    Deletes a store by its ID.
    Args:
        id (int): The ID of the store to delete.
        session (Session): The SQLAlchemy session to use for the delete.
    Returns:
        None
    Raises:
        HTTPException(404): If the store with the specified ID does not exist.
    """
    item = get_by_id(id, session)
    session.delete(item)

    session.commit()