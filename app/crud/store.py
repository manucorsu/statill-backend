from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.store import Store
from app.schemas.store import StoreCreate
from app.crud.user import get_by_id as get_user_by_id, get_all_by_store_id


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


def create(store_data: StoreCreate, user_id: int, session: Session):
    """
    Creates a new store in the database.
    Args:
        store_data (StoreCreate): The store data to create.
        session (Session): The SQLAlchemy session to use for the insert.
    Returns:
        int: The ID of the newly created store.
    """
    for index, ct in enumerate(store_data.closing_times):
        ot = store_data.opening_times[index]

        if (ct is None or ot is None) and ct != ot:
            raise HTTPException(
                400,
                detail="A store's opening time cannot be None if its closing time has a value (and vice-versa)",
            )

        if ct == ot:
            raise HTTPException(400, "A store cannot open and close at the same time")

    store = Store(**store_data.model_dump())

    session.add(store)
    session.flush()
    session.refresh(store)

    user = get_user_by_id(user_id, session)
    user.store_id = store.id
    user.store_role = "owner"

    session.commit()
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
    Deletes a store by its ID, cascading delete to products, sales, and products_sales, but not users.
    Args:
        id (int): The ID of the store to delete.
        session (Session): The SQLAlchemy session to use for the delete.
    Returns:
        None
    Raises:
        HTTPException(404): If the store with the specified ID does not exist.
    """
    item = get_by_id(id, session)

    # Delete all products associated with this store
    from app.models.product import Product

    products = session.query(Product).filter(Product.store_id == id).all()
    for product in products:
        session.delete(product)

    # Delete all sales associated with this store
    from app.models.sale import Sale
    from app.models.products_sales import ProductsSales

    sales = session.query(Sale).filter(Sale.store_id == id).all()
    for sale in sales:
        products_sales = (
            session.query(ProductsSales).filter(ProductsSales.sale_id == id).all()
        )
        for ps in products_sales:
            session.delete(ps)
        session.delete(sale)

    # Do NOT delete users, just disassociate them
    users = get_all_by_store_id(id, session)
    for user in users:
        user.store_id = None
        user.store_role = None

    session.delete(item)
    session.commit()
