from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from ...dependencies.db import get_db
from ...schemas.points import GetAllPointsResponse, GetUserPointsResponse, PointsRead
from ...schemas.general import SuccessfulResponse
from ...crud import points as crud
from ...crud import product as products_crud
from ...models.points import Points

name = "points"
router = APIRouter()


def __points_to_pointsread(p: Points):
    return PointsRead(id=p.id, store_id=p.store_id, user_id=p.user_id, amount=p.amount)


@router.get("/", response_model=GetAllPointsResponse)
def get_all_points(session: Session = Depends(get_db)):
    """
    Returns all points entries from the database.



    Args:
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        GetAllPointsResponse: A response model containing all points entries.
    """
    result = crud.get_all_points(session)
    return GetAllPointsResponse(
        data=[__points_to_pointsread(p) for p in result],
        message="Successfully retrieved all points entries.",
    )


@router.get("/store/{store_id}", response_model=GetUserPointsResponse)
def get_user_points(store_id: int, user_id: int, session: Session = Depends(get_db)):
    """
    Retrieves the points of a user in a specific store.


    Args:
        store_id (int): The ID of the store.
        user_id (int): The ID of the user. Goes in body for now and will later be extracted from the token.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        GetUserPointsResponse: A response model containing the user's points in the specified store.
    Raises:
        HTTPException(404): If the user or store does not exist, or if the user has no points in the store.
    """
    points = crud.get_user_points(user_id, store_id, session)
    return GetUserPointsResponse(
        data=__points_to_pointsread(points),
        message="Successfully retrieved user's points in the specified store.",
    )


@router.post(
    "/product/{product_id}", response_model=SuccessfulResponse, status_code=201
)
def buy_with_points(user_id: int, product_id: int, session: Session = Depends(get_db)):
    """
    Creates a sale where the user buys is buying the product using their points.


    Args:
        user_id (int): The ID of the user. Goes in body for now and will later be extracted from the token.
        product_id (int): The ID of the product to buy with points.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        SuccessfulResponse: A response model indicating the success of the operation.
    Raises:
        (various, including 400 and 404): If the user, product, or points entry does not exist, if the user does not have enough points, if the store does not have a points system, or if the specific product cannot be purchased with points.
    """
    product = products_crud.get_by_id(product_id, session)
    crud.buy_with_points(user_id, product, session)
    return SuccessfulResponse(data=None, message="Purchase with points successful.")


@router.get("/store/{id}/all", response_model=GetAllPointsResponse)
def get_points_by_store_id(id: int, session: Session = Depends(get_db)):
    """
    Retrieves all points by its store ID.



    Args:
        id (int): The ID of the store to retrieve its points.
        session (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetAllPointsResponse: A response containing a list of points with the specified store ID.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the store with the specified ID does not exist.
    """
    result = crud.get_all_by_store_id(id, session)
    return GetAllPointsResponse(
        successful=True,
        data=[__points_to_pointsread(p) for p in result],
        message=f"Successfully retrieved all Points with store id {id}.",
    )
