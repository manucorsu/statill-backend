from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models.user import User

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.dependencies.db import get_db

from app.schemas.product import (
    ProductCreate,
    GetAllProductsResponse,
    GetProductResponse,
    ProductUpdate,
)
from app.schemas.general import APIResponse

from app.crud import product as crud

import app.api.generic_tags as tags

from ...models.user import StoreRoleEnum

from .auth import get_current_user_require_active

from ...utils import owns_a_store_raise

name = "products"
router = APIRouter()


@router.get("/", response_model=GetAllProductsResponse, tags=tags.public)
def get_all_products(
    include_anonymized: bool = False, session: Session = Depends(get_db)
):
    """
    Retrieves all products from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.
        include_anonymized (bool): If set to `False`, soft-deleted products marked as `"Deleted Product"` will not be included in the result list. Default is `False`.

    Returns:
        GetAllProductsResponse: A response containing a list of all products.
    """
    result = crud.get_all(session=session, include_anonymized=include_anonymized)
    return GetAllProductsResponse(
        successful=True, data=result, message="Successfully retrieved all products."
    )


@router.get("/store/{id}", response_model=GetAllProductsResponse, tags=tags.public)
def get_products_by_store_id(
    id: int, session: Session = Depends(get_db), include_anonymized: bool = False
):
    """
    Retrieves a product by its store ID.

    Args:
        id (int): The ID of the store to retrieve its products.
        allow_anonymized (bool): If set to `False`, a 404 error will be raised if the product with the specified ID is marked as `"Deleted Product"`, just as if the product did not exist in the database. Default is `False`.
        session (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetAllProductsResponse: A response containing a list of products with the specified store ID.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the store with the specified ID does not exist.
    """

    result = crud.get_all_by_store_id(
        id, session, include_anonymized=include_anonymized
    )
    return GetAllProductsResponse(
        successful=True,
        data=result,
        message=f"Successfully retrieved all Products with store id {id}.",
    )


@router.get("/{id}", response_model=GetProductResponse, tags=tags.public)
def get_product_by_id(
    id: int, allow_anonymized: bool = False, session: Session = Depends(get_db)
):
    """
    Retrieves a product by its ID.

    Args:
        id (int): The ID of the product to retrieve.
        allow_anonymized (bool): If set to `False`, a 404 error will be raised if the product with the specified ID is marked as `"Deleted Product"`, just as if the product did not exist in the database. Default is `False`.
        session (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetProductResponse: A response containing the product with the specified ID.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the product with the specified ID does not exist.
    """

    result = crud.get_by_id(id, session, allow_anonymized=allow_anonymized)
    return GetProductResponse(
        successful=True,
        data=result,
        message=f"Successfully retrieved the Product with id {result.id}.",
    )


@router.post(
    "/", response_model=APIResponse, status_code=201, tags=tags.requires_active_user
)
def create_product(
    product: ProductCreate,
    session: Session = Depends(get_db),
    store_owner: User = Depends(get_current_user_require_active),
):
    """
    Creates a product in the authenticated user's store.

    Args:
        product (ProductCreate): The product data.
        session (Session): The SQLAlchemy session to use for the query.
        store_owner (User): The current authenticated active user who owns the store where the product will be created.
    Returns:
        APIResponse: A response containing the ID of the created product.
    """
    owns_a_store_raise(store_owner)
    product_id = crud.create(
        product_data=product, session=session, store_id=store_owner.store_id
    )
    return APIResponse(
        successful=True,
        data={"id": product_id},
        message=f"Successfully created the Product, which received id {product_id}.",
    )


@router.put("/{id}", response_model=APIResponse, tags=tags.requires_active_user)
def update_product(
    id: int,
    product: ProductUpdate,
    session: Session = Depends(get_db),
    store_owner: User = Depends(get_current_user_require_active),
):
    """
    Updates a product by its ID.

    Args:
        id (int): The ID of the product to update.
        product (ProductUpdate): The updated product data.
        session (Session): The SQLAlchemy session to use for the update.
        store_owner (User): The current authenticated active user who owns the store where the product will be updated.

    Returns:
        APIResponse: A response indicating the success of the update operation.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the product with the specified ID does not exist.
        HTTPException(403): If the authenticated user is not the owner of the store.
    """
    owns_a_store_raise(store_owner)
    p = crud.get_by_id(id, session, False)
    if p.store_id != store_owner.store_id:
        raise HTTPException(403, "You cannot modify this store's products")
    crud.update(id, product, session)
    return APIResponse(
        successful=True, data=None, message="Successfully updated the Product."
    )


@router.delete("/{id}", response_model=APIResponse, tags=tags.requires_active_user)
def delete_product(
    id: int,
    session: Session = Depends(get_db),
    store_owner: User = Depends(get_current_user_require_active),
):
    """
    Deletes a product by its ID.
    If the product is not in any sale, it will be erased from the database.
    If any sale contains any amount of the product, it will be anonymized instead.

    Args:
        id (int): The ID of the product to delete.
        session (Session): The SQLAlchemy session to use for the delete.

    Returns:
        APIResponse: A response indicating the success of the delete operation.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the product with the specified ID does not exist.
    """
    owns_a_store_raise(store_owner)
    crud.delete(id, session)
    return APIResponse(
        successful=True,
        data=None,
        message=f"Successfully deleted the Product with id {id}.",
    )
