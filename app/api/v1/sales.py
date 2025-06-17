from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.dependencies.db import get_db

from app.schemas.sale import SaleRead
from app.schemas.general import Message
from ...crud import product as crud

router = APIRouter()

@router.get("/", response_model=GetAllSalesResponse)
def get_sales(db: Session = Depends(get_db)):
    result = crud.get_all(db)
    return GetAllSalesResponse(
        successful=True, data=result, message="Successfully retrieved all Sales."
    )


@router.get("/id", response_model=GetSaleResponse)
def get_sale_by_id(id: int, db: Session = Depends(get_db)):
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
def update_sale(id: int, sale: SaleCreate, db: Session = Depends(get_db)):
    if id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id.")

    crud.update_by_id(id, product, db)
    return APIResponse(
        successful=True, data=None, message="Successfully updated the Sale."
    )


@router.delete("/", response_model=APIResponse)
def delete_sale_by_id(id: int, db: Session = Depends(get_db)):
    if id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id.")

    crud.delete_by_id(id, db)
    return APIResponse(
        successful=True,
        data=None,
        message=f"Successfully deleted the Sale with id {id}.",
    )

