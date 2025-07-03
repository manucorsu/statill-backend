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
    user = User(**user_data.model_dump(), role="buyer")

    session.add(user)
    session.commit()
    session.refresh(user)

    return int(user.id)
