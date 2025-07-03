from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.schemas.general import APIResponse
from sqlalchemy.exc import IntegrityError

# import logging

# logger = logging.getLogger(__name__)


def http_exception_handler(_: Request, ex: HTTPException):
    # logger.warning(f"HTTPException: {ex.detail} (status {ex.status_code}) at {request.url}")
    return JSONResponse(
        status_code=ex.status_code,
        content=dict(APIResponse(successful=False, data=dict(ex.detail), message=ex.detail)),
    )

def validation_exception_handler(_: Request, ex: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=dict(
            APIResponse(successful=False, data=dict(ex), message="Unprocessable Entry")
        ),
    )

def check_violation_handler(_: Request, ex: IntegrityError):
    return JSONResponse(
        status_code=422,
        content=dict(
            APIResponse(successful=False, data=dict(ex.detail), message="Request violated CHECK constraint")
        )
    )
