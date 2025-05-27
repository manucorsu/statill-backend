from fastapi import APIRouter
from . import status, products

router = APIRouter()

router.include_router(status.router, prefix="/status", tags=["status"])
router.include_router(products.router, prefix="/products", tags=["products"])
