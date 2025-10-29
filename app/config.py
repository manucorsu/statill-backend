from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from os import getenv
from email_validator import validate_email
from typing import Literal

load_dotenv()


class Settings(BaseSettings):
    mode: Literal["local", "render-dev", "render-prod"] = getenv("MODE")

    database_url: str = getenv("DATABASE_URL")
    frontend_origins: list[str] = getenv("FRONTEND_ORIGINS").split(",")

    jwt_secret: str = getenv("JWT_SECRET")
    jwt_algorithm: str = getenv("JWT_ALGORITHM")
    jwt_expiry: int = int(getenv("JWT_EXPIRY"))

    email_address: str = getenv("EMAIL_ADDRESS")
    email_app_password: str = getenv("EMAIL_APP_PASSWORD")
    smtp_host: str = getenv("SMTP_HOST")


settings = Settings()

assert settings.jwt_expiry > 1
validate_email(settings.email_address)

__BASE_URLS = {
    "local": "http://localhost:8000",
    "render-dev": "https://statill-api-dev.onrender.com",
    "render-prod": "https://statill-api.onrender.com",
}


def get_base_url():
    return __BASE_URLS[settings.mode]
