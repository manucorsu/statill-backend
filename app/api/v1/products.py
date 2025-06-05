from email.policy import HTTP
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.dependencies.db import get_db

from app.schemas.product import ProductRead, ProductCreate
from ...crud import product as crud

router = APIRouter()


@router.get("/", response_model=list[ProductRead])
def get_products(db: Session = Depends(get_db)):
    return crud.get_all(db)


@router.get("/id", response_model=ProductRead)
def get_product_by_id(id: int, db: Session = Depends(get_db)):
    if id <= 0:
        raise HTTPException(status_code="400", detail="Invalid id.")

    return crud.get_by_id(id, db)

@router.post("/")
def create_product(product: ProductCreate):
    return crud.create(product)