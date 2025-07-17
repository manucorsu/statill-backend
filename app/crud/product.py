from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.products_sales import ProductsSales
from app.schemas.product import ProductCreate, ProductUpdate
from . import store as stores_crud


def get_all(session: Session, include_anonymized: bool = False):
    """
    Retrieves all products from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.
        include_anonymized (bool): If set to `False`, soft-deleted products marked as `"Deleted Product"` will not be included in the result list. Default is `False`.
    Returns:
        list[Product]: A list of all products.
    """
    query = session.query(Product)

    if not include_anonymized:
        query = query.filter(Product.name != "Deleted Product")

    return query.all()


def get_by_id(id: int, session: Session, allow_anonymized: bool = False):
    """
    Retrieves a product by its ID.
    Args:
        id (int): The ID of the product to retrieve.
        session (Session): The SQLAlchemy session to use for the query.
        allow_anonymized (bool): If set to `False`, a 404 error will be raised if the product with the specified ID is marked as`"Deleted Product"`, just as if the product did not exist in the database. Default is `False`.
    Returns:
        Product: The product with the specified ID.
    Raises:
        HTTPException(404): If the product with the specified ID does not exist, or is a `"Deleted Product"` and `allow_anonymized` is set to `False`.
    """
    product = session.get(Product, id)
    if product is None or (product.name == "Deleted Product" and not allow_anonymized):
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
    if product_data.hidden == None:
        product_data.hidden = False
    if product_data.name == "Deleted Product":
        raise HTTPException(400, detail="Invalid product name.")

    stores_crud.get_by_id(
        product_data.store_id, session
    )  # Checks that the store exists. Extracting the id from the product_data is temporary and will only stay there until we do login

    product = Product(
        **product_data.model_dump(),
    )

    session.add(product)
    session.commit()
    session.refresh(product)
    return int(product.id)


def update(id: int, product_data: ProductUpdate, session: Session):
    """
    Updates a product by its ID.
    Args:
        id (int): The ID of the product to update.
        product_data (ProductUpdate): The updated product data.
        session (Session): The SQLAlchemy session to use for the update.
    Returns:
        None
    Raises:
        HTTPException(404): If the product with the specified ID does not exist.
    """
    product = get_by_id(id, session)

    if product_data.hidden == None:
        product_data.hidden = product.hidden

    updates = product_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(product, field, value)

    session.commit()


def delete(id: int, session: Session):
    """
    Deletes a product by its ID.

    If the product is not in any sale, it will be erased from the database.

    If any sale contains any amount of the product, it will be anonymized instead, meaning:
        * Its name, brand and description will be set to `"Deleted Product"`.
        * Its barcode data will be set to None.
        * Its quantity will permanently be 0.

    Args:
        id (int): The ID of the product to delete.
        session (Session): The SQLAlchemy session to use for the delete.
    Returns:
        None
    Raises:
        HTTPException(404): If the product with the specified ID does not exist.
    """
    item = get_by_id(id, session)
    in_sales = session.query(ProductsSales)

    if in_sales:
        item.name = "Deleted Product"
        item.brand = "Deleted Product"
        item.desc = "Deleted Product"
        item.barcode = None
        item.quantity = 0
    else:
        session.delete(item)

    session.commit()
