from fastapi import APIRouter, Depends

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