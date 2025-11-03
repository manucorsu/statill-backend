from __future__ import annotations
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from ...models.store import Store

from ...schemas.user import LoginResponse, Token
from ...schemas.general import SuccessfulResponse

from ...dependencies.db import get_db

import app.crud.user as user_crud

import app.security as security
from app.mailing import send_verification_code

from ...models.user import User
from ...models.verification_code import VerificationCode

from ...utils import utcnow
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException

from sqlalchemy.orm import Session

TOKEN_URL = "/api/v1/auth/token"
name = "auth"
router = APIRouter()
oauth2 = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)


@router.post("/token", response_model=LoginResponse)
def token(
    form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)
):
    """
    Authenticate a user and issue an access token.

    This endpoint handler performs authentication using form-encoded credentials
    (compatible with OAuth2PasswordRequestForm). It looks up the user by email,
    verifies the provided password against the stored hash, and, if valid,
    creates and returns a token wrapped in a LoginResponse.

    Args:
        form_data (OAuth2PasswordRequestForm): Dependency-injected form with
                'username' (email) and 'password' fields.
        session (Session): Database session dependency (provided by get_db).

    Returns:
        LoginResponse: On success, contains the issued token in `data` and a
            human-readable message describing the login success.

    Raises:
        HTTPException (401 Unauthorized): Raised when the user is not found or the
            password verification fails. The response includes a
            "WWW-Authenticate: Bearer" header.
    Notes:
        - Uses crud.get_by_email to retrieve the user record.
        - Uses verify_password to compare the plaintext password with the stored hash.
        - Uses create_token with the user's id as the token subject.
        - The returned message includes the user's email and indicates where the
          token is provided (in the `data` field).
        - Authentication and token creation side effects occur within this function.
    """

    user = user_crud.get_by_email(form_data.username, session, raise_404=False)
    if not user or not security.verify_password(
        plain_password=form_data.password, hashed_password=str(user.password)
    ):
        raise HTTPException(
            401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )  # más vague porque lean me dijo que no le diga nada al usuario en dos mil veinticuatro

    token = security.create_token(subject=user.id)
    return LoginResponse(
        data=Token(token=token),
        message=f"Logging into {user.email} successful: Token is in data",
    )


def get_current_user(token: str = Depends(oauth2), session: Session = Depends(get_db)):
    """
    # IMPORTANT:
    **In most cases you should use `get_current_user_require_active`.** Only use this if you specifically need to allow inactive users (e.g., for activation)
    Get the current authenticated user based on the provided JWT token.
    Endpoints that require auth `Depends` on this by adding `user: User = Depends(get_current_user)`
    as a Python parameter AFTER `session`
    #
    Args:
        token (str): The JWT token obtained from OAuth2 authentication. Defaults to Depends(oauth2).
        session (Session): The database session. Defaults to Depends(get_db).
    Returns:
        User: The authenticated user object.
    Raises:
        HTTPException: If the token is invalid or user is not found.
            - 404: User not found
            - 401: Invalid token (raised by decode_token)
    Dependencies:
        - oauth2: OAuth2 authentication scheme
        - get_db: Database session factory
    """

    payload = security.decode_token(token)  # raises if invalid
    user_id = int(payload.get("sub"))
    user = user_crud.get_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_user_require_active(
    user: User = Depends(get_current_user),
):
    """
    Get the current authenticated and active user.
    Endpoints that require an active user `Depends` on this by adding
    `user: User = Depends(get_current_user_require_active)` as a Python parameter AFTER `session`.

    Args:
        user (User): The authenticated user object obtained from get_current_user.
    Returns:
        User: The authenticated and active user object.
    Raises:
        HTTPException(403): If the user is not active (email not verified).
    """
    if not user.email_verified:
        raise HTTPException(status_code=403, detail="Forbidden: Inactive user")
    return user


def get_current_user_require_admin(
    user: User = Depends(get_current_user_require_active),
):

    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    return user


@router.patch("/activate", response_model=SuccessfulResponse)
def activate(
    code: str,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    verification = (
        session.query(VerificationCode)
        .filter(
            VerificationCode.code == code
            and VerificationCode.user_id == user.id
            and VerificationCode.type == "email"
        )
        .first()
    )

    if not verification:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    if verification.expires_at < utcnow():
        session.delete(verification)
        session.commit()
        raise HTTPException(status_code=400, detail="Code expired")

    user.email_verified = True
    session.delete(verification)
    session.commit()

    return SuccessfulResponse(data=None, message="User is now activated.")


@router.get("/send-email-verification-code", response_model=SuccessfulResponse)
def send_email_verification_code_endpoint(
    session: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    """
    Send an email verification code to the authenticated user.

    This endpoint triggers sending a verification code to the current user's
    email address by calling the helper send_verification_code. It is intended
    to be used as a FastAPI route handler relying on dependency-injected
    database session and authenticated user.

    Args:
        session (Session): Database session provided by the get_db dependency.
        user (User): Authenticated user object provided by the get_current_user dependency.

    Returns:
        SuccessfulResponse: A response object with message "Activation email sent."
        and no data payload.

    Side effects:
        - Sends an email (via send_verification_code).
        - May create or update verification-related records in the database.

    Raises:
        HTTPException or other exceptions propagated from send_verification_code
        on failure to generate or deliver the verification email.
    """

    send_verification_code(session, user, type="email")
    return SuccessfulResponse(data=None, message="Activation email sent.")
