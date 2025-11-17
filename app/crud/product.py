from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.products_sales import ProductsSales
from app.models.orders_products import OrdersProducts

from app.schemas.product import ProductCreate, ProductUpdate

from . import store as stores_crud, order as orders_crud, discount as discounts_crud


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


def get_all_by_store_id(id: int, session: Session, include_anonymized: bool = False):
    """
    Retrieves all products from the database by their store ID.
    Args:
        id (int): The ID of the store.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Product]: A list for the products with the store ID.
    Raises:
        HTTPException(404): If the store with the specified ID does not exist.
    """
    products = session.query(Product).filter(Product.store_id == id).all()

    if not include_anonymized:
        products = products.filter(Product.name != "Deleted Product")

    return products.all()


def create(product_data: ProductCreate, session: Session, store_id: int):
    """
    Creates a new product in the database.
    Args:
        product_data (ProductCreate): The product data to create.
        session (Session): The SQLAlchemy session to use for the insert.
        store_id (int): The ID of the store to which the product belongs.
    Returns:
        int: The ID of the newly created product.
    """
    if product_data.hidden == None:
        product_data.hidden = False
    if product_data.name == "Deleted Product":
        raise HTTPException(400, detail="Invalid product name.")

    stores_crud.get_by_id(
        store_id, session
    )  # Checks that the store exists. Extracting the id from the product_data is temporary and will only stay there until we do login

    product = Product(
        **product_data.model_dump(),
        store_id=store_id,
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
    Deletes a product by its ID. This will also delete any associated discounts.

    If the product is not in any sale or non-RECEIVED order it will be erased from the database.

    If any sale contains any amount of the product, it will be anonymized instead, meaning:
        * Its name, brand and description will be set to `"Deleted Product"`.
        * Its barcode data will be set to None.
        * Its quantity will permanently become 0.

    Args:
        id (int): The ID of the product to delete.
        session (Session): The SQLAlchemy session to use for the delete.
    Returns:
        None
    Raises:
        HTTPException(404): If the product with the specified ID does not exist.
        HTTPException(400): If the product is part of any pending or accepted (but not received) order.
    """
    product = get_by_id(id, session)
    orders = session.query(OrdersProducts).filter(OrdersProducts.product_id == id).all()
    sales = session.query(ProductsSales).filter(ProductsSales.product_id == id).all()
    discount = discounts_crud.get_by_product_id(id, session, raise_404=False)

    if discount:
        session.delete(discount)

    # Checks if the product is part of any pending or accepted order, and blocks deletion if so
    for op in orders:
        order = orders_crud.get_by_id(op.order_id, session)
        if order.status != orders_crud.StatusEnum.RECEIVED:
            raise HTTPException(
                400,
                "Cannot delete product that is part of a pending or accepted order. Please fulfill or cancel the order first.",
            )

    # If the product is part of any sale, anonymize it instead of deleting it
    if len(sales) > 0:
        product.name = "Deleted Product"
        product.brand = "Deleted Product"
        product.desc = "Deleted Product"
        product.barcode = None
        product.quantity = 0
    else:
        session.delete(product)

    session.commit()
