from fastapi import APIRouter
from . import status, products, sales, users, stores

router = APIRouter()

router.include_router(status.router, prefix="/status", tags=["status"])
router.include_router(products.router, prefix="/products", tags=["products"])
router.include_router(sales.router, prefix="/sales", tags=["sales"])
# router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(stores.router, prefix="/stores", tags=["stores"])