from fastapi import APIRouter, responses
from . import status, products, sales, users, stores

router = APIRouter()


@router.get("/docs", response_class=responses.RedirectResponse, status_code=308)
def get_docs_redirect():
    return "/docs"


@router.get("/redoc", response_class=responses.RedirectResponse, status_code=308)
def get_redoc_redirect():
    return "/redoc"


router.include_router(status.router, prefix="/status", tags=["status"])
router.include_router(products.router, prefix="/products", tags=["products"])
router.include_router(sales.router, prefix="/sales", tags=["sales"])
router.include_router(stores.router, prefix="/stores", tags=["stores"])
router.include_router(users.router, prefix="/users", tags=["users"])
