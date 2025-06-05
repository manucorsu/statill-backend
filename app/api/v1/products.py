from email.policy import HTTP
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.dependencies.db import get_db

from app.schemas.product import ProductRead
from ...crud import product

router = APIRouter()


@router.get("/", response_model=list[ProductRead])
def get_products(id: int | None = Query(default=None), db: Session = Depends(get_db)):
    return product.get_all(db)


@router.get("/id", response_model=ProductRead)
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    if id <= 0:
        raise HTTPException(status_code="400", detail="Invalid id.")

    return product.get_by_id(id, db)
