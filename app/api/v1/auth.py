import datetime

from ...schemas.user import LoginResponse, Token
from ...schemas.general import SuccessfulResponse

from ...dependencies.db import get_db

import app.crud.user as user_crud

from ...security import (
    verify_password,
    create_token,
    decode_token,
    generate_email_verification_code,
)

from ...models.user import User
from ...models.email_verification_code import EmailVerificationCode

from ...mailing import send_email

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
    if not user or not verify_password(
        plain_password=form_data.password, hashed_password=str(user.password)
    ):
        raise HTTPException(
            401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )  # más vague porque lean me dijo que no le diga nada al usuario en dos mil veinticuatro

    token = create_token(subject=user.id)
    return LoginResponse(
        data=Token(token=token),
        message=f"Logging into {user.email} successful: Token is in data",
    )


def get_current_user(token: str = Depends(oauth2), session: Session = Depends(get_db)):
    """
    Get the current authenticated user based on the provided JWT token.
    Endpoints that require auth `Depends` on this by adding `user: User = Depends(get_current_user)`
    as a Python parameter AFTER `session`

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

    payload = decode_token(token)  # raises if invalid
    user_id = int(payload.get("sub"))
    user = user_crud.get_by_id(user_id, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def __utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


@router.patch("/activate", response_model=SuccessfulResponse)
def activate(
    code: str,
    session: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    verification = (
        session.query(EmailVerificationCode)
        .filter(
            EmailVerificationCode.code == code
            and EmailVerificationCode.user_id == user.id
        )
        .first()
    )

    if not verification:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    if verification.expires_at < __utcnow():
        session.delete(verification)
        session.commit()
        raise HTTPException(status_code=400, detail="Code expired")

    user = user_crud.get_by_id(verification.user_id, session)

    user.email_verified = True
    session.delete(verification)
    session.commit()

    return SuccessfulResponse(data=None, message="User is now activated.")


def send_email_verification_code(session: Session, user: User):
    if user.email_verified:
        raise HTTPException(400, "User's email is already verified")

    session.query(EmailVerificationCode).filter(
        EmailVerificationCode.user_id == user.id
    ).delete()

    code = generate_email_verification_code()
    expires_at = __utcnow() + datetime.timedelta(minutes=30)

    verification = EmailVerificationCode(
        user_id=user.id, code=code, expires_at=expires_at
    )
    session.add(verification)
    session.commit()

    send_email(
        user,
        subject="Activá tu cuenta de Statill",
        htmlBody=f"""
                <html>
                <body>
                    <h1>Statill</h1>
                    <p>Tu código de activación es {code}</p>
                </body>
                </html>
               """,
    )  # body es temporal obviamente


@router.get("/send-email-verification-code", response_model=SuccessfulResponse)
def send_email_verification_code_endpoint(
    session: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    send_email_verification_code(session, user)
    return SuccessfulResponse(data=None, message="Activation email sent.")
