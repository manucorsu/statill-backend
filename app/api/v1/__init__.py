from fastapi import APIRouter
from . import (
    auth,
    status,
    products,
    sales,
    users,
    stores,
    orders,
    discounts,
    points,
    reviews,
    geo,
)

router = APIRouter()

routers_to_include = [
    auth,
    status,
    products,
    sales,
    users,
    stores,
    orders,
    discounts,
    points,
    reviews,
    geo,
]  # list of modules that have a router

for r_module in routers_to_include:
    module_router = r_module.router
    module_name = r_module.name

    assert isinstance(module_router, APIRouter)
    assert isinstance(module_name, str)

    router.include_router(module_router, prefix=f"/{module_name}", tags=[module_name])
