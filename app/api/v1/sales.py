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


@router.get("/", response_model=GetAllSalesResponse)
def get_sales(db: Session = Depends(get_db)):
    """
    Retrieves all sales from the database.

    (Will require auth in the future)
    (Will require admin role in the future)
    Args:
        db (Session): The SQLAlchemy session to use for the query.
    Returns:
        GetAllSalesResponse: A response containing a list of all sales.
    """
    sales = crud.get_all(db)
    result = [__sale_to_saleread(s, crud.get_ps_by_sale(s, db)) for s in sales]
    return GetAllSalesResponse(
        successful=True, data=result, message="Successfully retrieved all Sales."
    )


@router.get("/{id}", response_model=GetSaleResponse)
def get_sale_by_id(id: int, db: Session = Depends(get_db)):
    """
    Retrieves a sale by its ID.

    (Will require auth in the future)

    Args:
        **id (int): The ID of the sale to retrieve.**
        db (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetProductResponse: A response containing the sale with the specified ID.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the sale with the specified ID does not exist.
    """
    sale = crud.get_by_id(id, db)
    result = SaleRead(**sale.__dict__, products=crud.get_ps_by_sale(sale, db))
    return GetSaleResponse(
        successful=True,
        data=result,
        message=f"Successfully retrieved the Sale with id {result.id}.",
    )


@router.post("/", response_model=APIResponse, status_code=201)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    """
    Creates a sale.

    (Will require auth in the future)

    Args:
        sale (SaleCreate): The sale data.
        db (Session): The SQLAlchemy session to use for the query.
    """
    sale_id = crud.create_sale_with_products(sale, db)
    return APIResponse(
        successful=True,
        data={"id": sale_id},
        message=f"Successfully created the Sale, which received id {sale_id}.",
    )
