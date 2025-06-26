from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.dependencies.db import get_db

from app.schemas.product import (
    ProductCreate,
    GetAllProductsResponse,
    GetProductResponse,
)
from app.schemas.general import APIResponse

from app.crud import product as crud

router = APIRouter()


@router.get("/", response_model=GetAllProductsResponse)
def get_products(db: Session = Depends(get_db)):
    """
    Retrieves all products from the database.

    (Will require auth in the future)
    (Will require admin role in the future)

    Args:
        db (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetAllProductsResponse: A response containing a list of all products.
    """
    result = crud.get_all(db)
    return GetAllProductsResponse(
        successful=True, data=result, message="Successfully retrieved all products."
    )


@router.get("/{id}", response_model=GetProductResponse)
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    """
    Retrieves a product by its ID.

    (Will require auth in the future)

    Args:
        id (int): The ID of the product to retrieve.
        db (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetProductResponse: A response containing the product with the specified ID.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the product with the specified ID does not exist.
    """
    if id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id.")

    result = crud.get_by_id(id, db)
    return GetProductResponse(
        successful=True,
        data=result,
        message=f"Successfully retrieved the Product with id {result.id}.",
    )


@router.post("/", response_model=APIResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Creates a product.

    (Will require auth in the future)

    Args:
        product (ProductCreate): The product data.
        db (Session): The SQLAlchemy session to use for the query.
    """
    product_id = crud.create(product, db)
    return APIResponse(
        successful=True,
        data={"id": product_id},
        message=f"Successfully created the Product, which received id {product_id}.",
    )


@router.put("/{id}", response_model=APIResponse)
def update_product(id: int, product: ProductCreate, db: Session = Depends(get_db)):
    """
    Updates a product by its ID.

    (Will require auth in the future)
    
    Args:
        id (int): The ID of the product to update.
        product (ProductCreate): The updated product data.
        db (Session): The SQLAlchemy session to use for the update.
    
    Returns:
        APIResponse: A response indicating the success of the update operation.
    
    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the product with the specified ID does not exist.
    """
    if id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id.")

    crud.update_by_id(id, product, db)
    return APIResponse(
        successful=True, data=None, message="Successfully updated the Product."
    )


@router.delete("/{id}", response_model=APIResponse)
def delete_product_by_id(id: int, db: Session = Depends(get_db)):
    """
    Deletes a product by its ID.
    
    (Will require auth in the future)

    Args:
        id (int): The ID of the product to delete.
        db (Session): The SQLAlchemy session to use for the delete.
    
    Returns:
        APIResponse: A response indicating the success of the delete operation.
    
    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the product with the specified ID does not exist.
    """
    if id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id.")

    crud.delete_by_id(id, db)
    return APIResponse(
        successful=True,
        data=None,
        message=f"Successfully deleted the Product with id {id}.",
    )
