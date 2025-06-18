from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.dependencies.db import get_db

from app.schemas.general import APIResponse
from app.schemas.sale import SaleRead, SaleCreate, GetAllSalesResponse, GetSaleResponse
from app.schemas.general import Message
from ...crud import sale as crud

router = APIRouter()

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
    result = crud.get_all(db)
    return GetAllSalesResponse(
        successful=True, data=result, message="Successfully retrieved all Sales."
    )


@router.get("/id", response_model=GetSaleResponse)
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
    if id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id.")

    result = crud.get_by_id(id, db)
    return GetSaleResponse(
        successful=True,
        data=result,
        message=f"Successfully retrieved the Sale with id {result.id}.",
    )


@router.post("/", response_model=APIResponse, status_code=201)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    
    sale_id = crud.create(sale, db)
    return APIResponse(
        successful=True,
        data={"id": sale_id},
        message=f"Successfully created the Sale, which received id {sale_id}.",
    )


@router.put("/id", response_model=APIResponse)
def update_sale(id: int, sale: SaleCreate, db: Session = Depends(get_db)):}
    """
    Updates a sale by its ID.

    (Will require auth in the future)

    Args:
       id (int): The ID of the sale to update.
       sale (SaleCreate): The updated sale data.
       db (Session): The SQLAlchemy session to use for the update.
    
    Returns:
        APIResponse: A response indicating the success of the update operation.
    
    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the sale with the specified ID does not exist.
    """
    if id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id.")

    crud.update_by_id(id, product, db)
    return APIResponse(
        successful=True, data=None, message="Successfully updated the Sale."
    )


@router.delete("/", response_model=APIResponse)
def delete_sale_by_id(id: int, db: Session = Depends(get_db)):
    """
    Deletes a sale by its ID.
    (Will require auth in the future)

    Args:
        id (int): The ID of the sale to delete.
        db (Session): The SQLAlchemy session to use for the delete.

    Returns:
        APIResponse: A response indicating the success of the delete operation.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the sale with the specified ID does not exist.
    """
    if id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id.")

    crud.delete_by_id(id, db)
    return APIResponse(
        successful=True,
        data=None,
        message=f"Successfully deleted the Sale with id {id}.",
    )

