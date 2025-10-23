from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.review import Review
from app.schemas.review import ReviewRead, ReviewCreate, GetAllReviewsResponse, GetReviewResponse

from . import review as reviews_crud, store as stores_crud, user as users_crud

def get_all(session: Session):
    """
    Retrieves all reviews from the database.
    Args:
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        list[Review]: A list of all reviews.
    """
    return session.query(Review).all()

def get_by_id(id: int, session: Session):
    """
    Retrieves a review by its ID.
    Args:
        id (int): The ID of the review to retrieve.
        session (Session): The SQLAlchemy session to use for the query.
    Returns:
        Review: The review with the specified ID.
    Raises:
        HTTPException(404): If the review with the specified ID does not exist.
    """
    review = session.get(Review, id)
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

def get_reviews_by_user_id(user_id: int, session: Session):
    return session.query(Review).filter(Review.user_id == user_id).all()

def get_reviews_by_store_id(store_id: int, session: Session):
    return session.query(Review).filter(Review.store_id == store_id).all()

def create(user_id: int, review_data: ReviewCreate, session: Session):
    """
    Creates a new review in the database.
    Args:
        review_data (ReviewCreate): The review data to create.
        session (Session): The SQLAlchemy session to use for the insert.
    Returns:
        int: The ID of the newly created review.
    """

    stores_crud.get_by_id(
        review_data.store_id, session
    )  # Checks that the store exists. Extracting the id from the review_data is temporary and will only stay there until we do login

    users_crud.get_by_id(
        user_id, session
    )  # Checks that the user exists. Extracting the id is temporary and will only stay there until we do login

    review = Review(
        **review_data.model_dump(),
    )

    session.add(review)
    session.commit()
    session.refresh(review)
    return int(review.id)

def delete(id: int, session: Session):
    """
    Deletes a review by its ID.

    Args:
        id (int): The ID of the review to delete.
        session (Session): The SQLAlchemy session to use for the delete.
    Returns:
        None
    Raises:
        HTTPException(404): If the review with the specified ID does not exist.
    """
    review = get_by_id(id, session)
    session.delete(review)
    session.commit()