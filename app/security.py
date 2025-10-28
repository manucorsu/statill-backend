from argon2 import PasswordHasher
from datetime import datetime, timezone, timedelta
from .config import settings
import jwt
from fastapi import HTTPException

import secrets
import string

__ph = PasswordHasher()


def hash(password: str) -> str:
    """
    Hashes a password using `argon2-cffi`.

    Args:
        password (str): The plain text password to hash.
    Returns:
        str: The hashed password.
    """
    return __ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a hashed password.

    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (str): The hashed password to verify against.
    Returns:
        bool: True if the password matches, False otherwise.
    """
    try:
        return __ph.verify(hashed_password, plain_password)
    except:
        return False


def create_token(subject, expires_delta: int = settings.jwt_expiry) -> str:
    """
    Creates a JWT token.
    Args:
        subject (Any): (Any but will be converted to `str(subject)`) The subject of the token (usually a user id).
        expires_delta (int): The expiration time in minutes. Default is set in settings.
    Returns:
        str: The encoded JWT token.
    Raises:
        ValueError: If expires_delta is not a positive integer.
    """
    if expires_delta < 1:
        raise ValueError("expires_delta must be a positive integer")
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_delta)
    payload = {"sub": str(subject), "iat": now.timestamp(), "exp": expire.timestamp()}

    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token


def decode_token(token: str):
    """
    Decodes a JWT token.
    Args:
        token (str): The JWT token to decode.
    Returns:
        dict: The decoded token payload.
    Raises:
        HTTPException(401): If the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        return dict(payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def generate_email_verification_code():
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(32))
