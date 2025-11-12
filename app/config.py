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

    mailgun_url: str = getenv("MAILGUN_URL")
    mailgun_api_key: str = getenv("MAILGUN_API_KEY")
    mailgun_email_address: str = getenv("MAILGUN_EMAIL_ADDRESS")

    geoapify_api_key: str = getenv("GEOAPIFY_API_KEY")


settings = Settings()

assert settings.jwt_expiry > 1
