from datetime import timedelta

from ...schemas.general import SuccessfulResponse, APIResponse
from ...schemas.user import UserCreate, LoginResponse

from ...dependencies.db import get_db

from .users import create_user as create_user_endpoint

import app.crud.user as crud

from ...security import verify_password, create_token

from ...config import settings


from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException

from sqlalchemy.orm import Session


router = APIRouter()
oauth2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


@router.post("/", response_model=APIResponse, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    (Alias for users.create_user)
    Creates a user.

    Args:
        user (UserCreate): The User data.
        db (Session): The SQLAlchemy session to use for the query.
    Returns:
        APIResponse: A response indicating that the user was created successfully.
    """
    return create_user_endpoint(user, db)


@router.post("/login", response_model=LoginResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db)
):
    """
    Authenticate a user and issue an access token.
    This endpoint handler performs authentication using form-encoded credentials
    (compatible with OAuth2PasswordRequestForm). It looks up the user by email,
    verifies the provided password against the stored hash, and, if valid,
    creates and returns a token wrapped in a LoginResponse.
    Args:
        mform_data (OAuth2PasswordRequestForm): Dependency-injected form with
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

    user = crud.get_by_email(form_data.username, session, raise_404=False)
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
        data=token, message=f"Logging into {user.email} successful: Token is in data"
    )
