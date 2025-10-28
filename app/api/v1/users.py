from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from app.models.user import User

from ...schemas.general import APIResponse
from ...schemas.user import (
    UserCreate,
    GetAllUsersResponse,
    GetUserResponse,
    UserRead,
    Token,
    LoginResponse,
)
from ...dependencies.db import get_db


from sqlalchemy.orm import Session

from ...crud import user as crud

from pydantic import EmailStr

from .auth import get_current_user

name = "users"
router = APIRouter()


@router.get("/", response_model=GetAllUsersResponse)
def get_all(include_anonymized: bool = False, session: Session = Depends(get_db)):
    """
    Retrieves all users from the database.

    (Will require auth in the future)
    (Will require admin role in the future)
    Args:
        include_anonymized (bool): Whether to include users anonymized as "Deleted User".
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        GetAllUsersResponse: A response containing a list of all users.
    """
    users = crud.get_all(session, include_anonymized=include_anonymized)
    user_reads: list[UserRead] = []

    for user in users:
        user_reads.append(__user_to_userread(user))

    return GetAllUsersResponse(
        successful=True, data=user_reads, message="Successfully retrieved all Users."
    )


@router.get("/me", response_model=GetUserResponse)
def get_current_user_endpoint(user: User = Depends(get_current_user)):
    """
    Get the current authenticated user.
    This endpoint retrieves the User object for the currently authenticated user.
    Args:
        user (User): The current authenticated user object, obtained through dependency injection.
                     This is extracted from the JWT token in the request.
    Returns:
        User: The User object containing the authenticated user's information.
    """
    return GetUserResponse(
        successful=True,
        data=__user_to_userread(user),
        message="Succesfully retrieved the current user.",
    )


@router.get("/{id}", response_model=GetUserResponse)
def get_by_id(
    id: int,
    allow_anonymized: bool = False,
    session: Session = Depends(get_db),
):
    """
    Retrieves a user by their ID.

    (Will require auth in the future)

    Args:
        id (int): The ID of the user to retrieve.
        allow_anonymized (bool): Whether to include users anonymized as "Deleted User".
        session (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetUserResponse: A response containing the user with the specified ID.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the user with the specified ID does not exist.
    """
    result = crud.get_by_id(id, session, allow_anonymized=allow_anonymized)
    return GetUserResponse(
        successful=True,
        data=__user_to_userread(result),
        message="Successfully retrieved the User.",
    )


@router.get("/store/{id}", response_model=GetAllUsersResponse)
def get_by_store_id(
    id: int,
    allow_anonymized: bool = False,
    session: Session = Depends(get_db),
):
    """
    Retrieves a list of users by their store ID.

    (Will require auth in the future)

    Args:
        id (int): The ID of the store.
        allow_anonymized (bool): Whether to include users anonymized as "Deleted User".
        session (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetAllUsesrResponse: A response containing the users with the specified store ID.

    Raises:
        HTTPException(404): If the store with the specified ID does not exist.
    """
    result = crud.get_by_store_id(id, session, allow_anonymized=allow_anonymized)
    return GetAllUsersResponse(
        successful=True,
        data=[__user_to_userread(u) for u in result],
        message="Successfully retrieved the list of Users.",
    )


@router.get("/email/{email}", response_model=GetUserResponse)
def get_by_email(
    email: EmailStr,
    session: Session = Depends(get_db),
):
    """
    Retrieves the user with the specified email address.

    Args:
        email (EmailStr): The email address.
        session (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetUserResponse: A response containing the user with the specified email address.

    Raises:
        HTTPException(404): If the specified email does not exist.
    """
    user = crud.get_by_email(email, session, True)
    return GetUserResponse(
        successful=True,
        data=__user_to_userread(user),
        message=f"Successfully retrieved the user with email {email}.",
    )


@router.post("/", response_model=APIResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Creates a user.
    Args:
        user (UserCreate): The User data.
        db (Session): The SQLAlchemy session to use for the query.

    Returns:
        APIResponse: A response indicating that the user was created successfully.
    """
    user_id = crud.create(user, db)
    return APIResponse(
        successful=True,
        data={"id": user_id},
        message=f"Successfully created the User, which received id {user_id}.",
    )


def __user_to_userread(user: User):
    return UserRead(
        id=user.id,
        first_names=user.first_names,
        last_name=user.last_name,
        email=user.email,
        birthdate=str(user.birthdate),
        gender=str(user.gender.value),
        res_area=user.res_area,
        store_id=user.store_id,
        store_role=str(user.store_role.value) if user.store_role else None,
    )


@router.put("/{id}", response_model=APIResponse)
def update_user(id: int, user: UserCreate, db: Session = Depends(get_db)):
    """
    Updates a user by its ID.

    (Will require auth in the future)

    Args:
        id (int): The ID of the user to update.
        user (UserCreate): The updated user data.
        db (Session): The SQLAlchemy session to use for the update.

    Returns:
        APIResponse: A response indicating the success of the update operation.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the user with the specified ID does not exist.
    """
    crud.update(id, user, db)
    return APIResponse(
        successful=True, data=None, message="Successfully updated the User."
    )


@router.delete("/{id}", response_model=APIResponse)
def delete_user_by_id(id: int, db: Session = Depends(get_db)):
    """
    Deletes a user by its ID, or anonymizes them if referenced in ProductsSales.

    (Will require auth in the future)

    Args:
        id (int): The ID of the user to delete.
        session (Session): The SQLAlchemy session to use for the delete.

    Returns:
        APIResponse: A response indicating the success of the delete operation.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the user  with the specified ID does not exist.
    """
    crud.delete(id, db)
    return APIResponse(
        successful=True,
        data=None,
        message=f"Successfully deleted the User with id {id}.",
    )

