from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from os import getenv

load_dotenv()


class Settings(BaseSettings):
    database_url: str = getenv("DATABASE_URL")
    frontend_origins: list[str] = getenv("FRONTEND_ORIGINS").split(",")
    jwt_secret: str = getenv("JWT_SECRET")
    jwt_algorithm: str = getenv("JWT_ALGORITHM")
    jwt_expiry: int = int(getenv("JWT_EXPIRY"))


settings = Settings()

assert settings.jwt_expiry > 1
