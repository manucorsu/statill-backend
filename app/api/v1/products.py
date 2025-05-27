from fastapi import APIRouter
from ...crud import product
router = APIRouter()

@router.get("/")
def get_products():
    #product.get_all()
    return{}