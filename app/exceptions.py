from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.schemas.general import APIResponse
from sqlalchemy.exc import IntegrityError
import re


def http_exception_handler(_: Request, ex: HTTPException):
    return JSONResponse(
        status_code=ex.status_code,
        content=APIResponse(
            successful=False, data=str(ex), message=ex.detail
        ).model_dump(),
    )


def validation_exception_handler(_: Request, ex: RequestValidationError):
    errors = ex.errors()
    for err in errors:
        if "ctx" in err and "error" in err["ctx"]:
            err["ctx"]["error"] = str(
                err["ctx"]["error"]
            )  # odio este lenguaje parte 1000

    return JSONResponse(
        status_code=422,
        content=APIResponse(
            successful=False, data=ex.errors(), message="Unprocessable Entry"
        ).model_dump(),
    )


def check_violation_handler(_: Request, ex: IntegrityError):
    error_message = str(ex.orig) if hasattr(ex, "orig") else str(ex)
    match = re.search(
        r'violates check constraint "([^"]+)"', error_message, re.IGNORECASE
    )
    violated_constraint = match.group(1) if match else "unknown"

    return JSONResponse(
        status_code=422,
        content=APIResponse(
            successful=False,
            data={
                "error": error_message,
            },
            message=f"Request violated CHECK constraint",
        ).model_dump(),
    )
