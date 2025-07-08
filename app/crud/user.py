from sqlalchemy.orm import Session, object_mapper

from ..models.user import User

from fastapi import HTTPException

from ..schemas.user import *


def get_all(session: Session):
    """
    Retrieves all users from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[User]: A list of all users.
    """
    users = session.query(User).all()
    print(users)
    return users


def get_by_id(id: int, session: Session):
    """
    Retrieves a user by its ID.
    Args:
        id (int): The ID of the user to retrieve.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        User: The user with the specified ID.
    Raises:
        HTTPException(404): If the user with the specified ID does not exist.
    """
    if id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id.")

    user = session.get(User, id)
    if user is None:
        raise HTTPException(404, detail="User not found")

    return user


def create(user_data: UserCreate, session: Session):
    """
    Creates a new user in the database.
    Args:
        user_data (UserCreate): The user data to create.
        session (Session): The SQLAlchemy session to use for the insert.
    Returns:
        int: The ID of the newly created user.
    """
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
    user = get_by_id(id, session)

    updates = user_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(user, field, value)

    session.commit()


def delete(id: int, session: Session):
    """
    Deletes a user by its ID.
    Args:
        id (int): The ID of the user to delete.
        session (Session): The SQLAlchemy session to use for the delete.
    Returns:
        None
    Raises:
        HTTPException(404): If the user with the specified ID does not exist.
    """
    item = get_by_id(id, session)
    session.delete(item)

    session.commit()