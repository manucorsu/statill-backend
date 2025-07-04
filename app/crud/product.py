from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate


def get_all(session: Session):
    """
    Retrieves all products from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Product]: A list of all products.
    """
    return session.query(Product).all()


def get_by_id(id: int, session: Session):
    """
    Retrieves a product by its ID.
    Args:
        id (int): The ID of the product to retrieve.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        Product: The product with the specified ID.
    Raises:
        HTTPException(404): If the product with the specified ID does not exist.
    """
    product = session.get(Product, id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def create(product_data: ProductCreate, session: Session):
    """
    Creates a new product in the database.
    Args:
        product_data (ProductCreate): The product data to create.
        session (Session): The SQLAlchemy session to use for the insert.
    Returns:
        int: The ID of the newly created product.
    """
    product = Product(
        **product_data.model_dump(), store_id=2
    )  # este store_id=2 es temporal, queda hasta que hagamos para crear locales
    session.add(product)
    session.commit()
    session.refresh(product)
    return int(product.id)


def update(id: int, product_data: ProductCreate, session: Session):
    """
    Updates a product by its ID.
    Args:
        id (int): The ID of the product to update.
        product_data (ProductCreate): The updated product data.
        session (Session): The SQLAlchemy session to use for the update.
    Returns:
        None
    Raises:
        HTTPException(404): If the product with the specified ID does not exist.
    """
    product = get_by_id(id, session)

    updates = product_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(product, field, value)

    session.commit()


def delete(id: int, session: Session):
    """
    Deletes a product by its ID.
    Args:
        id (int): The ID of the product to delete.
        session (Session): The SQLAlchemy session to use for the delete.
    Returns:
        None
    Raises:
        HTTPException(404): If the product with the specified ID does not exist.
    """
    item = get_by_id(id, session)
    session.delete(item)

    session.commit()