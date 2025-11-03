from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.api.v1 import router as api_router
from .config import settings
from .exceptions import (
    http_exception_handler,
    validation_exception_handler,
    check_violation_handler,
)
import warnings
from sqlalchemy.exc import IntegrityError

from .api import generic_tags

warnings.simplefilter("always", DeprecationWarning)

openapi_tags = [
    {"name": t}
    for t in (
        generic_tags.PUBLIC,
        generic_tags.REQUIRES_AUTH,
        generic_tags.REQUIRES_ACTIVE_USER,
        generic_tags.REQUIRES_ADMIN,
    )
]  # generic tags are added here, router name-based tags are added in api/v1/__init__.py
# this way the user sees access requirements in the docs first, before the specific module names


app = FastAPI(
    title="Statill API",
    version="1.5.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_tags=openapi_tags,
    swagger_ui_parameters={
        "supportedSubmitMethods": []
    },  # disables "Try it out" because auth is broken in Swagger UI for some reason
    # (it refuses to send the token and always sends `Authorization: Bearer undefined`?)
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, check_violation_handler)
