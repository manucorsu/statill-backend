from ast import Store
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.dependencies.db import get_db

from app.schemas.store import (
    StoreCreate,
    GetAllStoresResponse,
    GetStoreResponse,
)
from app.schemas.general import APIResponse

from app.crud import store as crud

router = APIRouter()


@router.get("/", response_model=GetAllStoresResponse)
def get_stores(db: Session = Depends(get_db)):
    """
    Retrieves all stores from the database.

    (Will require auth in the future)
    (Will require admin role in the future)

    Args:
        db (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetAllStoresResponse: A response containing a list of all stores.
    """
    result = crud.get_all(db)
    return GetAllStoresResponse(
        successful=True, data=result, message="Successfully retrieved all stores."
    )


@router.get("/{id}", response_model=GetStoreResponse)
def get_store_by_id(id: int, db: Session = Depends(get_db)):
    """
    Retrieves a store by its ID.

    (Will require auth in the future)

    Args:
        id (int): The ID of the store to retrieve.
        db (Session): The SQLAlchemy session to use for the query.

    Returns:
        GetStoreResponse: A response containing the store with the specified ID.

    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the store with the specified ID does not exist.
    """
    if id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id.")

    result = crud.get_by_id(id, db)
    return GetStoreResponse(
        successful=True,
        data=result,
        message=f"Successfully retrieved the Store with id {result.id}.",
    )


@router.post("/", response_model=APIResponse, status_code=201)
def create_store(store: StoreCreate, db: Session = Depends(get_db)):
    """
    Creates a store.

    (Will require auth in the future)

    Args:
        store (StoreCreate): The store data.
        db (Session): The SQLAlchemy session to use for the query.
    """
    store_id = crud.create(store, db)
    return APIResponse(
        successful=True,
        data={"id": store_id},
        message=f"Successfully created the Store, which received id {store_id}.",
    )


@router.put("/{id}", response_model=APIResponse)
def update_store(id: int, store: StoreCreate, db: Session = Depends(get_db)):
    """
    Updates a store by its ID.

    (Will require auth in the future)
    
    Args:
        id (int): The ID of the store to update.
        store (StoreCreate): The updated store data.
        db (Session): The SQLAlchemy session to use for the update.
    
    Returns:
        APIResponse: A response indicating the success of the update operation.
    
    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the store with the specified ID does not exist.
    """
    if id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id.")

    crud.update(id, store, db)
    return APIResponse(
        successful=True, data=None, message="Successfully updated the Store."
    )


@router.delete("/{id}", response_model=APIResponse)
def delete_store_by_id(id: int, db: Session = Depends(get_db)):
    """
    Deletes a store by its ID.
    
    (Will require auth in the future)

    Args:
        id (int): The ID of the store to delete.
        db (Session): The SQLAlchemy session to use for the delete.
    
    Returns:
        APIResponse: A response indicating the success of the delete operation.
    
    Raises:
        HTTPException(400): If the provided ID is invalid (less than or equal to 0).
        HTTPException(404): If the store  with the specified ID does not exist.
    """
    if id <= 0:
        raise HTTPException(status_code=400, detail="Invalid id.")

    crud.delete(id, db)
    return APIResponse(
        successful=True,
        data=None,
        message=f"Successfully deleted the Store with id {id}.",
    )
