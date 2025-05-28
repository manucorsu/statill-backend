from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.db import get_db

from app.schemas.product import ProductRead
from ...crud import product

router = APIRouter()

@router.get("/", response_model=list[ProductRead])
def get_products(db: Session = Depends(get_db)):
    return product.get_all(db)