from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException

from app.models.user import User

from ...schemas.general import APIResponse
from ...schemas.user import UserCreate, GetAllUsersResponse, GetUserResponse, UserRead

from ...dependencies.db import get_db

from sqlalchemy.orm import Session

from ...crud import user as crud

router = APIRouter()


@router.get("/", response_model=GetAllUsersResponse)
def get_all(session: Session = Depends(get_db)):
    """
    Retrieves all users from the database.

    (Will require auth in the future)
    (Will require admin role in the future)
    Args:
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        GetAllUsersResponse: A response containing a list of all sales.
    """
    users = crud.get_all(session)
    user_reads: list[UserRead] = []

    for user in users:
        user_reads.append(__user_to_userread(user))

    return GetAllUsersResponse(
        successful=True, data=user_reads, message="Successfully retrieved all Users."
    )


@router.get("/{id}", response_model=GetUserResponse)
def get_by_id(id: int, session: Session = Depends(get_db)):
    """
    Retrieves a user by their ID.

    (Will require auth in the future)

    Args:
        id (int): The ID of the product to retrieve.
        db (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetUserResponse: A response containing the user with the specified ID.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the product with the specified ID does not exist.
    """
    result = crud.get_by_id(id, session)
    return GetUserResponse(
        successful=True,
        data=__user_to_userread(result),
        message="Successfully retrieved all Users.",
    )

@router.post("/", response_model=APIResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Creates a user.
    Args:
        user (UserCreate): The User data.
        db (Session): The SQLAlchemy session to use for the query.
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
        password=user.password,
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
    Deletes a user by its ID.
    
    (Will require auth in the future)

    Args:
        id (int): The ID of the user to delete.
        db (Session): The SQLAlchemy session to use for the delete.
    
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
