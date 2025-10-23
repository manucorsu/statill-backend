from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.models.review import Review

from app.schemas.review import (
    ReviewRead,
    GetReviewResponse,
    GetAllReviewsResponse,
    ReviewCreate,
)
from app.schemas.general import APIResponse

from app.crud import review as crud

name = "reviews"
router = APIRouter()

def __review_to_reviewread(r: Review):
    return ReviewRead(id=r.id, store_id=r.store_id, user_id=r.user_id, stars=r.stars, desc=r.desc)

@router.get("/", response_model=GetAllReviewsResponse)
def get_reviews(session: Session = Depends(get_db)):
    """
    Retrieves all reviews from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetAllReviewsResponse: A response containing a list of all reviews.
    """
    result = crud.get_all(session=session)
    return GetAllReviewsResponse(
        data=[__review_to_reviewread(r) for r in result],
        successful=True, message="Successfully retrieved all reviews."
    )


@router.get("/{id}", response_model=GetReviewResponse)
def get_review_by_id(id: int, session: Session = Depends(get_db)):
    """
    Retrieves a review by its ID.

    (Will require auth in the future)

    Args:
        id (int): The ID of the review to retrieve.
        session (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetReviewResponse: A response containing the review with the specified ID.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the review with the specified ID does not exist.
    """

    result = crud.get_by_id(id, session)
    return GetReviewResponse(
        successful=True,
        data=__review_to_reviewread(result),
        message=f"Successfully retrieved the Review with id {result.id}.",
    )


@router.get("/store/{id}", response_model=GetAllReviewsResponse)
def get_reviews_by_store_id(id: int, session: Session = Depends(get_db)):
    """
    Retrieves a list of reviews by its store ID.

    (Will require auth in the future)

    Args:
        id (int): The ID of the store to retrieve its reviews.
        session (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetAllReviewsResponse: A response containing a list of reviews with the specified store ID.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the store with the specified ID does not exist.
    """

    result = crud.get_reviews_by_store_id(id, session)
    return GetAllReviewsResponse(
        successful=True,
        data=[__review_to_reviewread(r) for r in result],
        message=f"Successfully retrieved all Reviews with store id {id}.",
    )


@router.get("/user/{id}", response_model=GetAllReviewsResponse)
def get_reviews_by_user_id(id: int, session: Session = Depends(get_db)):
    """
    Retrieves a list of reviews by its user ID.

    (Will require auth in the future)

    Args:
        id (int): The ID of the user to retrieve its reviews.
        session (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetAllReviewsResponse: A response containing a list of reviews with the specified user ID.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the user with the specified ID does not exist.
    """

    result = crud.get_reviews_by_user_id(id, session)
    return GetAllReviewsResponse(
        successful=True,
        data=[__review_to_reviewread(r) for r in result],
        message=f"Successfully retrieved all Reviews with user id {id}.",
    )


@router.post("/", response_model=APIResponse, status_code=201)
def create_review(
    user_id: int, review: ReviewCreate, session: Session = Depends(get_db)
):
    """
    Creates a review.

    (Will require auth in the future)

    Args:
        review (ReviewCreate): The review data.
        session (Session): The SQLAlchemy session to use for the query.
    """
    review_id = crud.create(user_id, review, session)
    return APIResponse(
        successful=True,
        data={"id": review_id},
        message=f"Successfully created the Review, which received id {review_id}.",
    )

@router.delete("/{id}", response_model=APIResponse)
def delete_review(id: int, db: Session = Depends(get_db)):
    """
    Deletes a review by its ID.

    (Will require auth in the future)

    Args:
        id (int): The ID of the review to delete.
        db (Session): The SQLAlchemy session to use for the delete.

    Returns:
        APIResponse: A response indicating the success of the delete operation.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the review with the specified ID does not exist.
    """
    crud.delete(id, db)
    return APIResponse(
        successful=True,
        data=None,
        message=f"Successfully deleted the Review with id {id}.",
    )
