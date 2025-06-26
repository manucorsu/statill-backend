from fastapi import APIRouter, Depends

from ...schemas.general import APIResponse
from ...schemas.user import UserCreate, GetAllUsersResponse, GetUserResponse

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
    result = crud.get_all(session)

    return GetAllUsersResponse(
        successful=True, data=result, message="Successfully retrieved all Users."
    )
