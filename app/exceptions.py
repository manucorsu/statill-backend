from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.schemas.general import APIResponse
from sqlalchemy.exc import IntegrityError
import re
# import logging

# logger = logging.getLogger(__name__)


def http_exception_handler(_: Request, ex: HTTPException):
    # logger.warning(f"HTTPException: {ex.detail} (status {ex.status_code}) at {request.url}")
    return JSONResponse(
        status_code=ex.status_code,
        content=APIResponse(successful=False, data=str(ex), message=ex.detail),
    )


def validation_exception_handler(_: Request, ex: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=dict(
            APIResponse(successful=False, data=str(ex), message="Unprocessable Entry")
        ),
    )


def check_violation_handler(_: Request, ex: IntegrityError):
    error_message = str(ex.orig) if hasattr(ex, "orig") else str(ex)
    match = re.search(r'violates check constraint "([^"]+)"', error_message, re.IGNORECASE)
    violated_constraint = match.group(1) if match else "unknown"
    
    return JSONResponse(
        status_code=422,
        content=dict(
            APIResponse(
                successful=False,
                data={"violated_constraint": violated_constraint, "error": error_message},
                message=f"Request violated {violated_constraint} CHECK constraint",
            )
        ),
    )
