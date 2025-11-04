from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models.user import User

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.dependencies.db import get_db

from app.schemas.general import APIResponse
from app.schemas.sale import (
    SaleCreate,
    GetAllSalesResponse,
    GetSaleResponse,
    SaleRead,
    ProductSale as ProductSaleSchema,
)
from ...crud import sale as crud
from ...models.sale import Sale
from ...models.products_sales import ProductsSales as ProductsSalesModel

import app.api.generic_tags as tags
from .auth import get_current_user_require_admin, get_current_user_require_active
from ...models.user import StoreRoleEnum

name = "sales"
router = APIRouter()


def __sale_to_saleread(sale: Sale, products: list[ProductsSalesModel]):
    products_as_schemas: list[ProductSaleSchema] = []
    for ps in products:
        products_as_schemas.append(
            ProductSaleSchema(product_id=ps.product_id, quantity=ps.quantity)
        )

    return SaleRead(
        id=sale.id,
        user_id=sale.user_id,
        store_id=sale.store_id,
        payment_method=sale.payment_method,
        timestamp=sale.timestamp,
        products=products_as_schemas,
    )


@router.get("/", response_model=GetAllSalesResponse, tags=tags.requires_admin)
def get_all_sales(
    db: Session = Depends(get_db), _: User = Depends(get_current_user_require_admin)
):
    """
    Retrieves all sales from the database.

    Args:
        db (Session): The SQLAlchemy session to use for the query.
        _ (User): The current active admin user. Unused, is only there to enforce admin requirement.
    Returns:
        GetAllSalesResponse: A response containing a list of all sales.
    """
    sales = crud.get_all(db)
    result = [__sale_to_saleread(s, crud.get_ps_by_sale(s, db)) for s in sales]
    return GetAllSalesResponse(
        successful=True, data=result, message="Successfully retrieved all Sales."
    )


@router.get("/{id}", response_model=GetSaleResponse, tags=tags.requires_admin)
def get_sale_by_id(id: int, db: Session = Depends(get_db)):
    """
    Retrieves a sale by its ID.

    Args:
        id (int): The ID of the sale to retrieve.
        db (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetSaleResponse: A response containing the sale with the specified ID.

    Raises:
        HTTPException(404): If the sale with the specified ID does not exist.
    """
    sale = crud.get_by_id(id, db)
    result = __sale_to_saleread(sale, crud.get_ps_by_sale(sale, db))
    return GetSaleResponse(
        successful=True,
        data=result,
        message=f"Successfully retrieved the Sale with id {result.id}.",
    )


@router.get(
    "/store/my", response_model=GetAllSalesResponse, tags=tags.requires_active_user
)
def get_my_store_sales(
    db: Session = Depends(get_db),
    store_owner: User = Depends(get_current_user_require_active),
):
    """
    Retrieves all sales for the store owned by the current user.

    Args:
        db (Session): The SQLAlchemy session to use for the query.
        store_owner (User): The current authenticated user.
    Returns:
        GetAllSalesResponse: A response containing a list of all sales for the admin's store.
    """
    sales = crud.get_all_by_store_owner(store_owner, db)
    result = [__sale_to_saleread(s, crud.get_ps_by_sale(s, db)) for s in sales]
    return GetAllSalesResponse(
        successful=True,
        data=result,
        message="Successfully retrieved all Sales for your store.",
    )


@router.post(
    "/", response_model=APIResponse, status_code=201, tags=tags.requires_active_user
)
def create_sale(
    sale: SaleCreate,
    db: Session = Depends(get_db),
    cashier: User = Depends(get_current_user_require_active),
):
    """
    Creates a sale.

    Args:
        sale (SaleCreate): The sale data.
        db (Session): The SQLAlchemy session to use for the query.
        cashier (User): The current authenticated user creating the sale. They must be a store cashier or owner in the store where the sale is being created.
    Raises:
        HTTPException(404): If the store with the specified ID does not exist.
        HTTPException(404): If the user with the specified ID does not exist.
        HTTPException(400): If a product does not belong to the store.
        HTTPException(400): If there is insufficient stock for a product.
        HTTPException(400): If the sale has no products.
    Returns:
        APIResponse: A response containing the ID of the created sale.
    """
    if (cashier.store_id != sale.store_id) or (
        cashier.store_role not in [StoreRoleEnum.OWNER, StoreRoleEnum.CASHIER]
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to create sales for this store",
        )

    if len(sale.products) == 0:
        raise HTTPException(status_code=400, detail="Sale must have at least 1 product")
    sale_id = crud.create(sale, db, using_points=False)
    return APIResponse(
        successful=True,
        data={"id": sale_id},
        message=f"Successfully created the Sale, which received id {sale_id}.",
    )
