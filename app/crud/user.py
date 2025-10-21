from sqlalchemy.orm import Session

from ..models.user import User
from . import store as stores_crud

from fastapi import HTTPException

from ..schemas.user import *
from datetime import date
from .sale import get_sales_by_user_id
from typing import overload, Literal


def is_anonymized(user: User):
    return bool(user.email == "deleted@example.com")


def get_all(session: Session, include_anonymized: bool = False):
    """
    Retrieves all users from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.
        include_anonymized (bool): Whether to include users anonymized as "Deleted User".
    Returns:
        list[User]: A list of all users.
    """
    query = session.query(User)
    if not include_anonymized:
        query = query.filter(User.first_names != "Deleted User")
    users = query.all()
    return users


def get_by_id(id: int, session: Session, allow_anonymized: bool = False) -> User:
    """
    Retrieves a user by their ID.

    Args:
        id (int): The ID of the user to retrieve.
        session (Session): The SQLAlchemy session to use for the query.
        allow_anonymized (bool): If set to `False`, a 404 error will be raised if the User with the specified ID is marked as `"Deleted User"`, just as if the user did not exist in the database. Default is `False`.
    Returns:
        User: The user with the specified ID.
    Raises:
        HTTPException(404): If the user with the specified ID does not exist, or is a `"Deleted User"` and `allow_anonymized` is set to `False`.
    """
    user = session.get(User, id)
    if user is None or (is_anonymized(user) and not allow_anonymized):
        raise HTTPException(404, detail="User not found")

    return user


def get_by_store_id(id: int, session: Session, allow_anonymized: bool = False):
    """
    Retrieves a list of users by their store ID.

    Args:
        id (int): The ID of the store.
        session (Session): The SQLAlchemy session to use for the query.
        allow_anonymized (bool): If set to `False`, a 404 error will be raised if the User with the specified store ID is marked as `"Deleted User"`, just as if the user did not exist in the database. Default is `False`.
    Returns:
        list[User]: The users with the specified store ID.
    Raises:
        HTTPException(404): If the store with the specified ID does not exist.
    """
    stores_crud.get_by_id(id, session)
    users = session.query(User).filter(User.store_id == id).all()
    return users


@overload
def get_by_email(email: str, session: Session, raise_404: Literal[True]) -> User: ...


@overload
def get_by_email(
    email: str, session: Session, raise_404: Literal[False]
) -> User | None: ...


def get_by_email(email: str, session: Session, raise_404: bool = True) -> User | None:
    """
    Retrieve a user from the database by their email address.

    Args:
        email (str): The email address of the user to retrieve.
        session (Session): The SQLAlchemy session to use for the database query.
        raise_404 (bool, optional): Whether to raise an HTTP 404 exception if the user is not found. Defaults to True.

    Returns:
        User or None: The user object if found, otherwise None (if raise_404 is False).

    Raises:
        HTTPException: If the email is invalid (400) or if no user is found and raise_404 is True (404).
    """
    user = session.query(User).filter(User.email == email).first()
    if user is None and raise_404:
        raise HTTPException(404, f"No user found with the {email} email address.")
    return user


def get_all_by_store_id(id: int, session: Session):
    """
    Retrieves all users from the database by their store ID.
    Args:
        id (int): The ID of the store.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[User]: A list fo the users wiith the store ID.
    Raises:
        HTTPException(404): If the store with the specified ID does not exist.
    """
    users = session.query(User).filter(User.store_id == id).all()
    result: list[User] = []
    for u in users:
        if u.email != "deleted@example.com":
            result.append(u)

    return result


def create(user_data: UserCreate, session: Session):
    """
    Creates a new user in the database.
    Args:
        user_data (UserCreate): The user data to create.
        session (Session): The SQLAlchemy session to use for the insert.
    Returns:
        int: The ID of the newly created user.
    """
    if user_data.email.endswith("example.com"):
        raise HTTPException(400, detail="Invalid email address.")

    if get_by_email(user_data.email, session, raise_404=False):
        raise HTTPException(400, detail="Email address already in use.")
    try:
        date.fromisoformat(user_data.birthdate)
    except ValueError:
        raise HTTPException(400, detail="Invalid birthdate.")

    user = User(**user_data.model_dump(), is_admin=False)

    session.add(user)
    session.commit()
    session.refresh(user)

    return int(user.id)


def update(id: int, user_data: UserCreate, session: Session):
    """
    Updates a user by its ID.
    Args:
        id (int): The ID of the user to update.
        user_data (UserCreate): The updated user data.
        session (Session): The SQLAlchemy session to use for the update.
    Returns:
        None
    Raises:
        HTTPException(404): If the user with the specified ID does not exist.
    """
    try:
        date.fromisoformat(user_data.birthdate)
    except ValueError:
        raise HTTPException(400, detail="Invalid birthdate.")
    
    user = get_by_id(id, session)

    updates = user_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(user, field, value)

    session.commit()


def delete(id: int, session: Session):
    """
    Deletes a user by its ID, or anonymizes them if referenced in ProductsSales.
    Args:
        id (int): The ID of the user to delete.
        session (Session): The SQLAlchemy session to use for the delete.
    Returns:
        None
    Raises:
        HTTPException(404): If the user with the specified ID does not exist.
    """
    user = get_by_id(id, session)
    if user.store_id is not None and user in get_all_by_store_id(
        user.store_id, session
    ):
        raise HTTPException(
            400,
            f"User must be dissasociated from store {user.store_id} before deleting them.",
        )

    has_sales = get_sales_by_user_id(id, session).__len__() > 0
    if has_sales:
        user.first_names = "Deleted User"
        user.last_name = "Deleted User"
        user.birthdate = date(1900, 1, 1)
        user.gender = "X"
        user.email = "deleted@example.com"
        user.password = "Deleted User"
        user.res_area = "Deleted User"
        user.store_id = None
        user.store_role = None
    else:
        session.delete(user)

    session.commit()
