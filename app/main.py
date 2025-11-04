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

from .api.generic_tags import (
    public,
    requires_auth,
    requires_active_user,
    requires_admin,
)
from fastapi.responses import JSONResponse

warnings.simplefilter("always", DeprecationWarning)

openapi_tags = [
    {"name": public[0], "description": "No se debe enviar ningún token."},
    {
        "name": requires_auth[0],
        "description": "En el header `Authorization` se debe enviar un token válido (formato: `Bearer <token>`) de un usuario autenticado (`/auth/token`).",
    },
    {
        "name": requires_active_user[0],
        "description": "En el header `Authorization` se debe enviar un token válido (formato: `Bearer <token>`) de un usuario autenticado (`/auth/token`) que haya verificado su mail a través de `/auth/activate`.",
    },
    {
        "name": requires_admin[0],
        "description": "En el header `Authorization` se debe enviar un token válido (formato: `Bearer <token>`) de un usuario autenticado (`/auth/token`) que haya verificado su mail a través de `/auth/activate` y que además tenga permisos de administrador. **NO LOS USEN PARA NADA EN EL FRONT.** (la mayoría son endpoints viejos que fueron reemplazados por nuevas versiones que implementan token o no son necesarios.)",
    },
]


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


@app.middleware("http")
async def remove_authorize_button_middleware(request, call_next):
    if request.url.path == "/openapi.json":
        # Get the OpenAPI schema
        openapi_schema = app.openapi()
        # Remove security schemes
        if (
            "components" in openapi_schema
            and "securitySchemes" in openapi_schema["components"]
        ):
            del openapi_schema["components"]["securitySchemes"]
        return JSONResponse(content=openapi_schema)
    response = await call_next(request)
    return response
