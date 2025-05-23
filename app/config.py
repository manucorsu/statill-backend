from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from os import getenv

load_dotenv()


class Settings(BaseSettings):
    database_url: str = getenv("DATABASE_URL")
    frontend_origins: list[str] = getenv("FRONTEND_ORIGINS").split(",")


settings = Settings()
