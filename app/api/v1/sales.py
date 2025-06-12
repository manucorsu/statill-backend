from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.dependencies.db import get_db

from app.schemas.sale import SaleRead
from app.schemas.general import Message
from ...crud import product as crud

router = APIRouter()

@router.get("/", response_model=list[SaleRead])
def get_sales(db: Session = Depends(get_db)):
    return crud.get_all(db)


@router.get("/id", response_model=SaleRead)
def get_sale_by_id(id: int, db: Session = Depends(get_db)):
    if id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id.")

    return crud.get_by_id(id, db)
