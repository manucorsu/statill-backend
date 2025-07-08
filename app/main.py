from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.api.v1 import router as api_router
from .config import settings
from .exceptions import http_exception_handler, validation_exception_handler, check_violation_handler
import warnings
from sqlalchemy.exc import IntegrityError

warnings.simplefilter("always", DeprecationWarning)

app = FastAPI(title="Statill API", version="0.2.0")

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
