from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...models.user import User

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from app.models.user import User

from ...schemas.general import APIResponse
from ...schemas.user import (
    UserCreate,
    GetAllUsersResponse,
    GetUserResponse,
    UserRead,
    UserUpdate,
)
from ...dependencies.db import get_db


from sqlalchemy.orm import Session

from ...crud import user as crud

from pydantic import EmailStr

from .auth import (
    get_current_user,
    get_current_user_require_active,
    get_current_user_require_admin,
)
import app.api.generic_tags as tags
from ...utils import owns_specified_store_raise

name = "users"
router = APIRouter()


@router.get("/", response_model=GetAllUsersResponse, tags=tags.requires_admin)
def get_all_users(
    include_anonymized: bool = False,
    session: Session = Depends(get_db),
    _: User = Depends(get_current_user_require_admin),
):
    """
    Retrieves all users from the database.

    Args:
        include_anonymized (bool): Whether to include users anonymized as "Deleted User".
        session (Session): The SQLAlchemy session to use for the query.
        _ (User): The current active admin user. Unused, is only there to enforce admin requirement.
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


@router.get("/me", response_model=GetUserResponse, tags=tags.requires_auth)
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


@router.get("/{id}", response_model=GetUserResponse, tags=tags.requires_admin)
def get_user_by_id(
    id: int,
    allow_anonymized: bool = False,
    session: Session = Depends(get_db),
    _: User = Depends(get_current_user_require_admin),
):
    """
    Retrieves a user by their ID.

    Args:
        id (int): The ID of the user to retrieve.
        allow_anonymized (bool): Whether to include users anonymized as "Deleted User".
        session (Session): The SQLAlchemy session to use for the query.
        _ (User): The current active admin user. Unused, is only there to enforce admin requirement.

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


@router.get("/store/{id}", response_model=GetAllUsersResponse, tags=tags.requires_admin)
def get_users_by_store_id(
    id: int,
    allow_anonymized: bool = False,
    session: Session = Depends(get_db),
    _: User = Depends(get_current_user_require_admin),
):
    """
    Retrieves a list of users by their store ID.

    Args:
        id (int): The ID of the store.
        allow_anonymized (bool): Whether to include users anonymized as "Deleted User".
        session (Session): The SQLAlchemy session to use for the query.
        _ (User): The current active admin user. Unused, is only there to enforce admin requirement.

    Returns:
        GetAllUsersResponse: A response containing the users with the specified store ID.

    Raises:
        HTTPException(404): If the store with the specified ID does not exist.
    """
    result = crud.get_by_store_id(id, session, allow_anonymized=allow_anonymized)
    return GetAllUsersResponse(
        successful=True,
        data=[__user_to_userread(u) for u in result],
        message="Successfully retrieved the list of Users.",
    )


@router.get(
    "/store/my", response_model=GetAllUsersResponse, tags=tags.requires_active_user
)
def get_my_store_users(
    session: Session = Depends(get_db),
    store_owner: User = Depends(get_current_user_require_active),
):
    """
    Retrieves all users for the store owned by the current user.

    Args:
        session (Session): The SQLAlchemy session to use for the query.
        store_owner (User): The current authenticated user.
    Returns:
        GetAllUsersResponse: A response containing a list of all users for the store owned by the user.
    """
    owns_specified_store_raise(store_owner, store_owner.store_id, session)
    users = crud.get_by_store_id(store_owner.store_id, session, allow_anonymized=False)
    user_reads: list[UserRead] = []

    for user in users:
        user_reads.append(__user_to_userread(user))

    return GetAllUsersResponse(
        successful=True,
        data=user_reads,
        message="Successfully retrieved all Users for your store.",
    )


@router.get("/email/{email}", response_model=GetUserResponse, tags=tags.requires_admin)
def get_user_by_email(
    email: EmailStr,
    session: Session = Depends(get_db),
    _: User = Depends(get_current_user_require_admin),
):
    """
    Retrieves the user with the specified email address.

    Args:
        email (EmailStr): The email address.
        session (Session): The SQLAlchemy session to use for the query.
        _ (User): The current active admin user. Unused, is only there to enforce admin requirement.

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


@router.post("/", response_model=APIResponse, status_code=201, tags=tags.public)
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
        email_verified=user.email_verified,
    )


@router.put("/{id}", response_model=APIResponse, tags=tags.requires_admin)
def update_user_by_id(
    id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user_require_admin),
):
    """
    Updates a user by its ID.

    Important:
        * if the email is changed, the user will need to verify their new email address.
        * **the password cannot be changed via this endpoint!** Use reset-password instead.

    Args:
        id (int): The ID of the user to update.
        user (UserUpdate): The updated user data.
        db (Session): The SQLAlchemy session to use for the update.
        _ (User): The current active admin user. Unused, is only there to enforce admin requirement.

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


@router.put("/me", response_model=APIResponse, tags=tags.requires_active_user)
def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_require_active),
):
    """
    Updates the current authenticated user's information.

    Important:
        * if the email is changed, the user will need to verify their new email address.
        * **the password cannot be changed via this endpoint!** Use reset-password instead.

    Args:
        user_update (UserUpdate): The updated user data.
        db (Session): The SQLAlchemy session to use for the update.
        current_user (User): The current authenticated active user.

    Returns:
        APIResponse: A response indicating the success of the update operation.

    Raises:
        HTTPException(404): If the current user does not exist (should not happen).
    """
    crud.update(current_user.id, user_update, db)
    return APIResponse(
        successful=True,
        data=None,
        message="Successfully updated your User information.",
    )


@router.delete("/{id}", response_model=APIResponse, tags=tags.requires_admin)
def delete_user_by_id(
    id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user_require_admin),
):
    """
    Deletes a user by its ID, or anonymizes them if referenced in ProductsSales.

    Args:
        id (int): The ID of the user to delete.
        session (Session): The SQLAlchemy session to use for the delete.
        _ (User): The current active admin user. Unused, is only there to enforce admin requirement.

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


@router.delete("/me", response_model=APIResponse, tags=tags.requires_auth)
def delete_current_user(
    session: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_require_active),
):
    """
    Deletes the current authenticated user, or anonymizes them if referenced in ProductsSales.

    Args:
        session (Session): The SQLAlchemy session to use for the delete.
        current_user (User): The current authenticated user.
    Returns:
        APIResponse: A response indicating the success of the delete operation.
    """
    crud.delete(current_user.id, session)
    return APIResponse(
        successful=True,
        data=None,
        message="Successfully deleted your User account.",
    )


@router.get("/{id}/name", tags=tags.public)
def get_first_names_by_id(id: int, session: Session = Depends(get_db)):
    result = crud.get_first_names_by_id(id, session)
    return APIResponse(
        successful=True,
        data=result,
        message=f"Successfully got the first name of user {id}",
    )
