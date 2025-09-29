from fastapi import APIRouter, responses
from . import status, products, sales, users, stores, orders, discounts

router = APIRouter()

routers_to_include = [
    status,
    products,
    sales,
    users,
    stores,
    orders,
    discounts,
]  # list of modules that have a router

for r_module in routers_to_include:
    router.include_router(
        r_module.router, prefix=f"/{r_module.name}", tags=[r_module.name]
    )


@router.get("/docs", response_class=responses.RedirectResponse, status_code=308)
def get_docs_redirect():
    return "/docs"


@router.get("/redoc", response_class=responses.RedirectResponse, status_code=308)
def get_redoc_redirect():
    return "/redoc"
