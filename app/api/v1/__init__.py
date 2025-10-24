from fastapi import APIRouter, responses
from . import status, products, sales, users, stores, orders, discounts, points, reviews

router = APIRouter()

routers_to_include = [
    status,
    products,
    sales,
    users,
    stores,
    orders,
    discounts,
    points,
    reviews,
]  # list of modules that have a router

for r_module in routers_to_include:
    module_router = r_module.router
    module_name = r_module.name

    assert isinstance(module_router, APIRouter)
    assert isinstance(module_name, str)

    router.include_router(module_router, prefix=f"/{module_name}", tags=[module_name])


@router.get("/docs", response_class=responses.RedirectResponse, status_code=308)
def get_docs_redirect():
    return "/docs"


@router.get("/redoc", response_class=responses.RedirectResponse, status_code=308)
def get_redoc_redirect():
    return "/redoc"
