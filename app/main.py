from fastapi import FastAPI
from app.api.v1 import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from .config import settings

app = FastAPI(title="Statill API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
