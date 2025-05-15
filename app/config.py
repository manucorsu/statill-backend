from pydantic import BaseSettings
from dotenv import load_dotenv
from os import getenv

load_dotenv()


class Settings(BaseSettings):
    database_url: str = getenv("DATABASE_URL")


settings = Settings()
